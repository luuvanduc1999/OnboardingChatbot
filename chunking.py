import copy
import unicodedata
import uuid
import re
import xmltodict
import zipfile
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from pathlib import Path
from typing import Any, List, Optional, Union
import json
import roman

# Constants for splitting titles, list parsing, and mapping custom symbols
TITLE_COMMA_SPLIT = "#|#"
LIST_LEVEL_PREFIX = '<w:ilvl w:val="'
IMPORTANT_LIST_TYPES = ["decimal", "lowerRomain", "upperRoman"]
CUSTOM_LIST_SYMBOL_MAPS = {"": "•", "\uf02d": "-"}

# Data class for storing list paragraph information
class ListParagraphInfo:
  li_id: str
  li_value: Any
  li_level: str
  li_type: str

  def __init__(self, li_id, li_value, li_level, li_type):
    self.li_id = li_id
    self.li_value = li_value
    self.li_level = li_level
    self.li_type = li_type

# Data class for parsed list items
class ParseListItem:
  _id: str
  level: int
  title: str
  body_text: str = ""
  nested_list: List[Any] = None
  list_item_value: Any
  list_item_id: Any
  is_important: bool = False
  page_number: Optional[int] = 0

  def __init__(self, lvl: int, title: str, text: str):
    self._id = uuid.uuid4().hex
    self.title = title
    self.body_text = text
    self.level = lvl

# Data class for parsing context (headings, lists, tables)
class ParseContext:
  _id: str
  level: int
  title: str = ""
  body_text: str = ""
  is_heading: bool
  is_list: bool
  parent_ctx: Any = None
  nested_list: List['ParseListItem'] = None
  page_number: Optional[int] = 0
  should_keep_full_text: bool = False
  is_table: bool

  def __init__(self, lvl: int, is_heading: bool, is_list: bool = False, title=None, is_table=False):
    self._id = uuid.uuid4().hex
    self.level = lvl
    self.is_heading = is_heading
    self.is_list = is_list
    self.is_table = is_table
    if title:
      self.title = title

# Main class for extracting and chunking document structure
class StructExtract:
  def __init__(self, path: Path, title='', chunk_size: int = 200):
    self.chunk_size = chunk_size
    self.title = title
    self.with_heading = False
    self.list_marks = {}
    self.list_id_to_ctx = {}
    self.numeric_styles = {}
    self.font_levels = {}
    self.headings: List[ParseContext] = []
    self.head_on_work: Optional[ParseContext] = None
    self.previous_context: Optional[ParseContext] = None
    self.page_number = 1

    self.document = Document(path)
    self.main()

  def main(self):
    self.set_up_font_size()
    self.parse_document()

    for element in self.elements:
      if isinstance(element, Paragraph):
        self.update_page_number(element)
      self.split_element_content(element)

    if self.head_on_work and self.head_on_work not in self.headings:
      self.headings.append(self.head_on_work)
    if self.previous_context:
      new_context = self.append_body_or_break(text="")
      if new_context:
        self.headings.append(self.head_on_work)
    final_headings = []
    for h in self.headings:
      body = h.body_text.strip()
      if not body and not h.nested_list:
        continue
      h.body_text = body
      final_headings.append(h)
    self.headings = final_headings
    self.build_chunks()

  def build_chunks(self):
    """
    Build output chunks from parsed headings and lists.
    """
    chunks = []
    standalone_heading = None
    level_head_titles = {}

    def prepare_heading(heading: ParseContext):
      level_head_titles[str(heading.level)] = heading.body_text
      for i in range(1, 4):
        key_lvl = str(i)
        if i > heading.level and key_lvl in level_head_titles:
          del level_head_titles[key_lvl]

    def build_title():
      titles = []
      for i in range(standalone_heading.level):
        lvl_str = str(i + 1)
        if lvl_str not in level_head_titles:
          continue
        titles.append(level_head_titles[lvl_str])
      return TITLE_COMMA_SPLIT.join(titles)

    def append_chunks(next_chunks: List):
      for n_chunk in next_chunks:
        n_chunk['title'] = (
          build_title() if standalone_heading else n_chunk.get('title') or ''
        )
        chunks.append(n_chunk)

    for heading in self.headings:
      heading.title = heading.title or self.title

      _id = uuid.uuid4().hex
      content = heading.body_text.strip()
      next_chunk = {
        'header': f'{_id}0',
        'title': heading.title,
        'text': content,
        'is_table': heading.is_table,
        'page_number': heading.page_number,
      }
      if heading.should_keep_full_text:
        next_chunk['should_keep_full_text'] = True

      if not heading.nested_list:
        if heading.is_heading and heading.level != 999:
          prepare_heading(heading)
          standalone_heading = heading
          continue
        append_chunks([next_chunk] if content else [])
        continue
      merged = self.merge_pieces(_id, heading, is_root=True)
      if not merged or len(merged) == 0:
        continue
      if len(heading.nested_list) == 1:
        append_chunks(self.merge_content_by_max_length(next_chunk, merged))
        continue
      if content:
        append_chunks([next_chunk])
      append_chunks(merged)
    idx = 1
    final_chunks = []
    for chunk in chunks:
      if not chunk['text'] or not chunk['text'].strip():
        continue
      chunk['index'] = idx
      chunk['title'] = (
        self.beautify_title(chunk['title'])
        if chunk.get('title')
        else self.title
      )
      chunk['title'] = chunk['title']
      idx += 1
      final_chunks.append(chunk)
    self.chunks = []
    for chunk in final_chunks:
      end_of_chunk = chunk.get('should_keep_full_text', None)
      if end_of_chunk == True:
        end_of_chunk = False
      else:
        end_of_chunk = True
      text = chunk['text']
      if len(text) < 5:
        continue
      self.chunks.append({
        'title': chunk['title'],
        'text': chunk['text'],
        'index': len(self.chunks),
        'page': chunk.get('page_number', 1),
        'end': end_of_chunk
      })
      self.chunks[-1]['end'] = True

  def merge_content_by_max_length(self, existence, next_merged):
    """
    Merge content pieces by chunk size.
    """
    out = [existence]
    if not existence:
      out[0] = {'text': ''}
    for item in next_merged:
      next_text = item['text'].strip()
      self.to_next_piece(out, next_text)
    return out

  def to_next_piece(self, out, next_text):
    """
    Add next_text to the last chunk or create a new chunk if size exceeded.
    """
    if len(out) == 0:
      out.append({'text': ''})
    next_text = next_text.strip()
    last_item = out[-1]
    if len(last_item['text'].split()) + len(next_text.split()) > self.chunk_size:
      out.append({'text': next_text})
      return
    if not last_item['text'].strip():
      last_item['text'] = next_text
    else:
      last_item['text'] = '\n'.join([last_item['text'].strip(), next_text])

  def merge_pieces(self, _id, heading: ParseContext, is_root=False):
    """
    Recursively merge nested list items into chunks.
    """
    if not heading.nested_list or len(heading.nested_list) == 0:
      return []
    idx = 1
    out = []

    def _get_header():
      return TITLE_COMMA_SPLIT.join([_id, str(idx)])

    previous_is_nested = False
    for i, item in enumerate(heading.nested_list):
      content = item.body_text.strip()
      if content:
        if previous_is_nested:
          out.append({'text': content})
        elif not item.nested_list:
          self.to_next_piece(out, content)
          idx += 1

      if item.nested_list:
        item.title = heading.title
        next_merged = self.merge_pieces(_get_header(), item, is_root=True)
        if len(heading.nested_list) == 1:
          self.to_next_piece(out, content)
          last_item = out[-1] if len(out) > 0 else None
          out = self.merge_content_by_max_length(last_item, next_merged)
        else:
          if i == 0 or previous_is_nested:
            if content:
              out.append({'text': content})
            last_item = out[-1] if len(out) > 0 else None
            next_merged = self._merge_content_by_max_length(
              last_item, next_merged
            )
            if len(next_merged) > 1:
              next_merged = [
                {
                  **item_merged,
                  'title': self.get_last_sentences(item_merged['text']),
                }
                for item_merged in next_merged
              ]
            if last_item:
              out += next_merged[1:]
            else:
              out += next_merged
          else:
            out += self.merge_content_by_max_length(
              {'text': content}, next_merged
            )
        previous_is_nested = True
        continue
      previous_is_nested = False
    if is_root:
      out = [
        {
          **item,
          'title': heading.title
          if ('title' not in item or not item['title'])
          else f"{heading.title}\n{item['title']}",
        }
        for item in out
      ]
    return out

  def get_last_sentences(self, text: str):
    """
    Get the last sentence from text.
    """
    sentences = self.split_into_sentences(text)
    if not sentences:
      return ''
    return sentences[-1]

  def beautify_title(self, title: str):
    """
    Remove duplicate parts from title.
    """
    parts = title.split(TITLE_COMMA_SPLIT)
    if len(parts) <= 1:
      return title
    unique = {}
    for part in parts:
      if part in unique:
        continue
      nested_parts = [item.strip()
              for item in part.split('\n') if item.strip()]
      for nested_part in nested_parts:
        if nested_part in unique:
          continue
        unique[nested_part] = {}
    return '\n'.join([key for key in unique])

  def no_accent_vietnamese(self, s: str):
    """
    Remove Vietnamese accents from string.
    """
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

  def split_element_content(self, element: Union[Paragraph, Table]):
    """
    Process and split content of a document element (paragraph or table).
    """
    is_skip_element = self.is_skip_element(element)
    if is_skip_element:
      return

    if isinstance(element, Table):
      table_markdown = self.convert_table_to_markdown(element)
      self.append_body_or_break(table_markdown)
      if not self.is_single_cell_table(element):
        self.head_on_work.should_keep_full_text = True
      return

    text = element.text.strip()
    style = element.style.name.lower()
    text = unicodedata.normalize("NFC", text)
    is_heading = style.startswith("heading")
    is_custom_list = style.startswith("list")
    is_default_list = self.get_list_item_value(
      element._p.xml, only_validate=True
    )
    is_normal_paragraph = not (
      is_heading or is_custom_list or is_default_list)
    li_id = self.get_list_item_id(element._p.xml)
    if not is_normal_paragraph:
      ctx = self.bind_heading_or_list_to_context(element)
      if li_id and li_id not in self.list_id_to_ctx:
        self.list_id_to_ctx[li_id] = ctx._id
      return

    previous_is_nested_heading = (
      self.head_on_work
      and isinstance(self.head_on_work.nested_list, list)
      and len(self.head_on_work.nested_list) > 0
    )
    last_ctx = self.get_last_context()
    is_last_ctx_not_important = (
      not last_ctx
      or not hasattr(last_ctx, "is_important")
      or not last_ctx.is_important
    )
    if previous_is_nested_heading:
      if not is_last_ctx_not_important:
        last_ctx.body_text = "\n".join([last_ctx.body_text, text])
        return
      self.to_next_context(
        self.head_on_work.level,
        self.head_on_work.title,
        self.head_on_work.is_heading,
      )
    self.append_body_or_break(text, True)

  def bind_heading_or_list_to_context(self, paragraph: Paragraph):
    """
    Bind heading or list paragraph to context.
    """
    text = paragraph.text.strip()
    style = paragraph.style.name.lower()

    list_item_info: Optional[ListParagraphInfo] = self.get_list_item_value(
      paragraph._p.xml
    )
    li_id = None
    li_value = None
    if list_item_info:
      li_id = list_item_info.li_id
      li_value = list_item_info.li_value

    if style.startswith("heading"):
      lvl = int(self.trim_only_number(style.split("heading ")[1]))
      self.to_next_context(lvl, text, True)
      self.head_on_work.body_text = text
      return self.head_on_work

    para_level = None
    if style.startswith("list"):
      try:
        para_level = int(style.split("list ")[1])
      except:
        if style == "list paragraph":
          if list_item_info:
            para_level = self.get_list_level(paragraph)
          else:
            para_level = 999
        else:
          if self.head_on_work:
            para_level = self.head_on_work.level + 1
          else:
            para_level = 0

    if para_level is None:
      if list_item_info:
        para_level = self.get_list_level(paragraph)
      else:
        para_level = 999

    if list_item_info:
      is_important = list_item_info.li_type in IMPORTANT_LIST_TYPES
    else:
      is_important = False

    is_important = (
      list_item_info.li_type in IMPORTANT_LIST_TYPES if list_item_info else False
    )
    if li_value:
      text = f"{li_value} {text}"

    next_list_item = ParseListItem(
      para_level, self.head_on_work.title if self.head_on_work else "", text
    )
    next_list_item.list_item_value = li_value
    next_list_item.list_item_id = li_id
    next_list_item.is_important = is_important
    next_list_item.page_number = self.page_number

    if not self.head_on_work:
      self.head_on_work = self.init_context_with_meta(999, True)
      self.head_on_work.nested_list = [next_list_item]
      return next_list_item

    if not self.head_on_work.nested_list:
      prev_title = (
        self.previous_context.title
        if self.previous_context
        else self.head_on_work.title
      )
      next_text = self.previous_context.body_text if self.previous_context else ""
      self.previous_context = None

      self.to_next_context(para_level, prev_title, False)
      self.head_on_work.body_text = next_text

      self.head_on_work.nested_list = [next_list_item]
      return next_list_item

    last_ctx = self.get_last_context()
    is_lower_level = para_level > self.head_on_work.nested_list[0].level
    list_container = self.head_on_work.nested_list[
      len(self.head_on_work.nested_list) - 1
    ]
    if not is_lower_level and li_id != last_ctx.list_item_id:
      if li_id not in self.list_marks:
        is_lower_level = True
        list_container = last_ctx
      elif is_important and li_id in self.list_id_to_ctx:
        list_container = self.find_context_contain_list(
          self.list_id_to_ctx[li_id]
        )
    if li_value is None:
      try:
        prev_li_value = self.get_previous_list_item_level()
        if type(prev_li_value) != type(li_value):
          list_container = last_ctx
        else:
          list_container = list_container
      except:
        pass

    if is_lower_level:
      prev_sentences = self.split_into_sentences(list_container.body_text)
      list_item = ParseListItem(
        para_level,
        f"{list_container.title}#{prev_sentences[-1]}",
        text,
      )
      list_item.list_item_value = li_value
      list_item.list_item_id = li_id
      if not list_container.nested_list:
        list_container.nested_list = [list_item]
      else:
        list_container.nested_list = list_container.nested_list + [list_item]

      list_item.page_number = self.page_number
      return list_item

    if list_container.nested_list:
      list_container.nested_list.append(next_list_item)
    elif not is_important:
      list_container.nested_list = [next_list_item]
    else:
      self.head_on_work.nested_list.append(next_list_item)

    return next_list_item

  def split_into_sentences(self, text: str):
    """
    Split text into sentences using delimiters.
    """
    delimiters = ".", "?", "!"
    regex_pattern = "|".join(map(re.escape, delimiters))
    return re.split(regex_pattern, text)

  def get_previous_list_item_level(self):
    """
    Get the previous list item level.
    """
    ctx = self.get_last_context()
    try:
      parts = ctx.list_item_value.split(".")
      return int(parts[0]) if len(parts) > 1 else ctx.list_item_value
    except:
      return ctx.list_item_value

  def find_context_contain_list(self, _id):
    """
    Find context containing a list by id.
    """
    list_ctx = self.headings + [self.head_on_work]

    def recursive_find(ctx: ParseContext):
      if ctx._id == _id:
        return True
      if not ctx.nested_list:
        return False
      for item in ctx.nested_list:
        found = recursive_find(item)
        if not found:
          continue
        if found is True:
          return ctx
        return found
    for ctx in list_ctx:
      exist = recursive_find(ctx)
      if not exist:
        continue
      if exist is True:
        return ctx
      return exist
    return None

  def get_last_context(self):
    """
    Get the last context in the current heading.
    """
    if not self.head_on_work:
      return None
    ctx = self.head_on_work
    while ctx.nested_list:
      ctx = ctx.nested_list[-1]
    return ctx

  def get_list_level(self, paragraph: Paragraph):
    """
    Get the list level from paragraph XML.
    """
    flat_xml = str(paragraph._p.xml)
    lvl_idx = flat_xml.find(LIST_LEVEL_PREFIX)
    start_lvl_idx = lvl_idx + len(LIST_LEVEL_PREFIX)
    end_lvl_idx = flat_xml[start_lvl_idx:].find('"')
    level = int(flat_xml[start_lvl_idx: start_lvl_idx + end_lvl_idx])
    return level

  def trim_only_number(self, text: str):
    """
    Remove all non-numeric characters from text.
    """
    return re.sub("[^0-9]", "", text)

  def get_list_item_value(self, xml, only_validate=False):
    """
    Get the value of a list item from XML.
    """
    list_info = self.get_list_struct(xml)
    if not list_info:
      return False
    if only_validate:
      return True
    _id = list_info["id"]
    lvl = list_info["lvl"]
    if _id not in self.list_marks:
      self.list_marks[_id] = {}
    if lvl not in self.list_marks[_id]:
      self.list_marks[_id][lvl] = 0
    self.list_marks[_id][lvl] += 1
    full_value = []
    i = 0
    max_lvl = 1
    try:
      max_lvl = int(lvl) + 1
    except:
      pass
    last_type = None
    last_format = None
    prefix = self.get_mark_prefix(self.get_list_item_format(_id, '0'))
    suffix = ''
    while i < max_lvl:
      lvl_str = str(i)
      if lvl_str not in self.list_marks[_id]:
        next_value = self.get_default_mark_value(_id, lvl_str)
      else:
        next_value = self.list_marks[_id][lvl_str]

      last_type = self.get_node_object(
        self.numeric_styles, [_id, lvl_str, 'w:numFmt', '@w:val']
      )
      if not last_type:
        return ListParagraphInfo(
          li_id=_id, li_level=lvl, li_value=next_value, li_type=last_type
        )
      last_format = self.get_list_item_format(_id, lvl_str)
      v, suffix = self.get_value_by_type(last_type, last_format, next_value)
      full_value.append(v)
      i += 1
    if last_type == "bullet":
      value = (
        full_value[-1].__str__() if len(full_value) > 0 else ""
      )
    elif self.is_list_item_alone(last_format):
      value = (
        prefix
        + (
          full_value[-1].__str__()
          if len(full_value) > 0
          else ''
        )
        + suffix
      )
    else:
      value = prefix + '.'.join([str(item) for item in full_value]) + suffix
    return ListParagraphInfo(
      li_id=_id, li_level=lvl, li_value=value, li_type=last_type
    )

  def get_mark_prefix(self, text):
    """
    Get prefix from list item format.
    """
    if not text:
      return ""
    parts = text.split("%")
    return parts[0]

  def is_list_item_alone(self, text):
    """
    Check if list item format is alone.
    """
    return len(re.findall(r"[\%0-9]{2}", text)) == 1

  def get_default_mark_value(self, _id, lvl):
    """
    Get default value for a list mark.
    """
    li_value = self.get_node_object(
      self.numeric_styles, [_id, lvl, "w:start", "@w:val"])
    try:
      li_value = int(li_value)
    except:
      li_value = 1
    return li_value

  def get_value_by_type(self, li_type, li_format, li_value):
    """
    Get value by list type and format.
    """
    suffix = self.get_mark_suffix(li_format)
    if li_type == "bullet":
      if li_format in CUSTOM_LIST_SYMBOL_MAPS:
        li_format = CUSTOM_LIST_SYMBOL_MAPS[li_format]
      return li_format, suffix

    if li_type == "lowerRoman":
      return roman.toRoman(li_value), suffix

    if li_type == "upperRoman":
      return roman.toRoman(li_value), suffix

    if li_type == "upperLetter":
      return chr(li_value + 64), suffix

    if li_type == "lowerLetter":
      return chr(li_value + 96), suffix

    if li_type == "decimal":
      return li_value, suffix

    return li_value, suffix

  def get_list_item_format(self, _id, lvl):
    """
    Get list item format from numbering styles.
    """
    return self.get_node_object(self.numeric_styles, [_id, lvl, "w:lvlText", "@w:val"])

  def get_list_item_id(self, xml: str, only_validate=False):
    """
    Get list item id from XML.
    """
    list_info = self.get_list_struct(xml)
    if not list_info:
      return False
    if only_validate:
      return True

  def get_list_struct(self, xml: str):
    """
    Parse XML to get list structure (id and level).
    """
    xml_dict = xmltodict.parse(xml)
    num_meta = self.get_node_object(
      xml_dict,
      [
        'w:p',
        'w:pPr',
        'w:numPr',
      ],
    )
    if not num_meta:
      return None
    return {
      'id': num_meta['w:numId']['@w:val'],
      'lvl': num_meta['w:ilvl']['@w:val'],
    }

  def convert_table_to_markdown(self, table: Table):
    """
    Convert a table to markdown format.
    """
    is_single_cell_table = self.is_single_cell_table(table)
    if is_single_cell_table:
      text = table.rows[0].cells[0].text.strip()
      text = unicodedata.normalize('NFC', text)
      return text

    texts = []
    first_row = True
    num_cols = 0
    merged_cells_by_col = {}
    number_of_column = len(table.columns)
    for c in range(number_of_column):
      merged_cells_by_col[c] = 0
    for row in table.rows:
      cells = row.cells
      for idx, cell in enumerate(cells):
        if idx > 0 and cell == cells[idx - 1]:
          merged_cells_by_col[idx] += 1
    number_of_row = len(table.rows)
    merged_columns = [
      c for c, v in merged_cells_by_col.items() if v == number_of_row]
    for row in table.rows:
      row_texts = []
      cells = row.cells
      for idx, cell in enumerate(cells):
        if idx in merged_columns:
          continue
        else:
          row_texts.append(self.normalize_cell_content(cell.text) or '---')
      if len(row_texts) < num_cols:
        row_texts += [' '] * (num_cols - len(row_texts))
      if row_texts:
        texts.append('|' + '|'.join(row_texts) + '|')
      if first_row:
        texts.append('|' + '|'.join(['---'] * len(row_texts)) + '|')
        first_row = False
        num_cols = len(row_texts)
    text = '\n'.join(texts)
    text = unicodedata.normalize('NFC', text)
    text = '\n' + text
    return text

  def normalize_cell_content(self, text: str):
    """
    Normalize cell content for markdown.
    """
    return text.strip().replace('|', '\|')

  def is_single_cell_table(self, table: Table):
    """
    Check if table has only one cell.
    """
    number_of_row = len(table.rows)
    number_of_column = len(table.columns)
    return number_of_row == 1 and number_of_column == 1

  def is_skip_element(self, element: Union[Paragraph, Table]):
    """
    Determine if an element should be skipped.
    """
    if isinstance(element, Table):
      return False
    text = element.text.strip()
    if text == '':
      return True

    style = element.style.name.lower()
    if style == 'title':
      self.title = text
      return True

    if self.with_heading == False:
      self.chunk_by_font_size_level(element)
      return True

    return False

  def chunk_by_font_size_level(self, paragraph: Paragraph):
    """
    Chunk paragraphs by font size level if no headings.
    """
    text = paragraph.text.strip()
    font_size = self.get_paragraph_font_size(paragraph)
    if font_size is not None and font_size in self.font_levels:
      font_level = self.font_levels[font_size]
    else:
      font_level = len(self.font_levels.keys())
    is_heading = font_level < len(self.font_levels.keys())
    if is_heading:
      self.to_next_context(font_level, text, True)
      return
    self.append_body_or_break(text, is_default=True)

  def append_body_or_break(self, text, is_default=False, is_table=False):
    """
    Append text to current context or break into new context if chunk size exceeded.
    """
    next_text = self.get_queued_text(text, is_default, is_table=is_table)
    new_context = False
    if not self.head_on_work:
      self.head_on_work = self.init_context_with_meta(
        999, True, is_table=is_table)
    if self.head_on_work.is_heading and self.head_on_work.level != 999:
      if self.head_on_work not in self.headings:
        self.headings.append(self.head_on_work)
      self.head_on_work = self.init_context_with_meta(
        999, False, is_table=is_table)
    if (
      len(self.head_on_work.body_text.split()) + len(next_text.split())
      > self.chunk_size
    ):
      if self.head_on_work:
        if self.head_on_work not in self.headings:
          self.headings.append(self.head_on_work)
        self.head_on_work = self.clone_to_continue_context(self.head_on_work)
        self.head_on_work.page_number = self.page_number
        new_context = True
      else:
        self.head_on_work = self.init_context_with_meta(
          999, False, False, is_table=is_table)
    self.head_on_work.body_text = (
      self.head_on_work.body_text + f'\n{next_text}'
    ).strip()
    return new_context

  def clone_to_continue_context(self, context: ParseContext):
    """
    Clone context for continuing chunking.
    """
    new_ctx = ParseContext(context.level, context.is_heading, context.is_list)
    new_ctx.title = context.title
    return new_ctx

  def get_queued_text(self, text, is_default=False, is_table=False):
    """
    Get text queued for the next context.
    """
    lvl = 999
    is_heading = False
    if self.head_on_work:
      lvl = self.head_on_work.level
      is_heading = self.head_on_work.is_heading
    if is_default:
      lvl = 999
      is_heading = False
    next_text = ''
    if self.previous_context:
      next_text = self.previous_context.body_text
    self.previous_context = self.init_context_with_meta(
      lvl, is_heading, is_table=is_table)
    self.previous_context.body_text = text
    self.previous_context.title = (
      self.head_on_work.title if self.head_on_work else self.title
    )
    return next_text

  def to_next_context(self, next_level: int, text: str, is_heading: bool):
    """
    Move to the next context (heading or list).
    """
    if self.previous_context:
      self.head_on_work.body_text = '\n'.join(
        [self.head_on_work.body_text, self.previous_context.body_text]
      )
      self.previous_context = None

    if not self.head_on_work:
      next_ctx = self.init_context_with_meta(
        next_level, is_heading, not is_heading
      )
      next_ctx.title = self.title
      self.head_on_work = next_ctx
      return self.head_on_work

    if self.head_on_work not in self.headings:
      self.headings.append(self.head_on_work)

    next_ctx = self.init_context_with_meta(
      next_level, is_heading, not is_heading)

    if next_level > self.head_on_work.level:
      next_ctx.parent_ctx = self.head_on_work
      next_ctx.level = next_level if is_heading else next_level - 1
      next_ctx.title = self.build_distinct_title(
        [item for item in [self.head_on_work.title, text] if item.strip()]
      )
    elif self.head_on_work.parent_ctx:
      next_ctx.title = self.build_distinct_title(
        [
          item
          for item in [self.head_on_work.parent_ctx.title, text]
          if item.strip()
        ]
      )
    else:
      next_ctx.title = self.title
    if self.head_on_work.parent_ctx:
      self.head_on_work.parent_ctx = None
    self.head_on_work = next_ctx
    return self.head_on_work

  def build_distinct_title(self, items):
    """
    Build a distinct title from a list of items.
    """
    distinct = {}
    for item in items:
      parts = item.split(TITLE_COMMA_SPLIT)
      for part in parts:
        if not part:
          continue
        distinct[part] = {}

    return TITLE_COMMA_SPLIT.join([key for key in distinct])

  def init_context_with_meta(
    self, lvl: int, is_heading: bool, is_list: bool = False, title=None, is_table=False
  ):
    """
    Initialize a new parsing context.
    """
    ctx = ParseContext(lvl=lvl, is_heading=is_heading,
               is_list=is_list, title=title, is_table=is_table)
    ctx.page_number = self.page_number
    return ctx

  def update_page_number(self, paragraph: Paragraph):
    """
    Increase page number by 1 when match page break.
    """
    for run in paragraph.runs:
      if "<w:lastRenderedPageBreak/>" in run.element.xml:
        self.page_number += 1
        return
      if "w:br" in run.element.xml and 'type="page"' in run.element.xml:
        self.page_number += 1
        return

  def parse_document(self):
    """
    Flatten all Paragraph and Table into self.elements list.
    """
    self.elements: list[Union[Paragraph, Table]] = []
    if self.document.sections:
      for section in self.document.sections:
        for item in section.iter_inner_content():
          self.elements.append(item)
    else:
      for item in self.document.iter_inner_content():
        self.elements.append(item)

  def set_up_font_size(self):
    """
    Find all font size in document and set up font levels.
    """
    font_size_dict = {}
    for paragraph in self.document.paragraphs:
      font_size = self.get_paragraph_font_size(paragraph)
      if font_size is not None:
        if font_size not in font_size_dict:
          font_size_dict[font_size] = 1
        else:
          font_size_dict[font_size] += 1
      text = paragraph.text.strip()
      if not text:
        continue
      style = paragraph.style.name.lower()
      if style == "title":
        self.title = text
        continue
      if style.startswith("heading"):
        self.with_heading = True
    self.font_size_dict = font_size_dict
    self.font_levels = {}
    if self.with_heading == True:
      return
    body_font = {
      "size": None,
      "exist": None,
    }
    for font_size in font_size_dict:
      if body_font["exist"] is None or body_font["exist"] < font_size_dict[font_size]:
        body_font["size"] = font_size
        body_font["exist"] = font_size_dict[font_size]
    list_font_size = [font_size for font_size in font_size_dict]
    list_font_size.sort(reverse=True)
    for index, font_size in enumerate(list_font_size, start=1):
      self.font_levels[font_size] = index
      if font_size == body_font["size"]:
        break

  def get_paragraph_font_size(self, paragraph: Paragraph):
    """
    Get font size from paragraph.
    """
    for run in paragraph.runs:
      if run.font.size:
        return run.font.size
    return paragraph.style.font.size

  def get_numbering_style(self, path: Path):
    """
    Get numbering style from document.
    """
    num_to_abstract = {}
    with zipfile.ZipFile(path) as zip:
      info = zip.NameToInfo.get('word/numbering.xml')
      if info is None:
        return None
      xml_content = zip.read('word/numbering.xml')
      xml_dict = xmltodict.parse(xml_content.decode('utf-8'))
      list_styles = self.get_node_object(
        xml_dict, ['w:numbering', 'w:abstractNum'])
      if not list_styles:
        return None
      abstract_num_info = {}
      numeric_definition = self.get_node_object(
        xml_dict, ['w:numbering', 'w:abstractNum'])
      if isinstance(numeric_definition, dict):
        numeric_definition = [numeric_definition]
      for item in numeric_definition:
        list_level = item['w:lvl']
        if isinstance(list_level, dict):
          list_level = [list_level]
        lvl_info = {}
        for lvl in list_level:
          lvl_info[lvl['@w:ilvl']] = lvl
        abstract_num_info[item['@w:abstractNumId']] = lvl_info
      numeric_values = self.get_node_object(xml_dict, ['w:numbering', 'w:num'])
      if isinstance(numeric_values, dict):
        numeric_values = [numeric_values]
      for item in numeric_values:
        abstract_val = item['w:abstractNumId']['@w:val']
        abstract_val = (
          abstract_num_info[abstract_val]
          if abstract_val in abstract_num_info
          else None
        )
        num_to_abstract[item['@w:numId']] = abstract_val
      num_to_abstract = copy.deepcopy(num_to_abstract)
    return num_to_abstract

  def get_node_object(self, obj: dict, path: List[str]):
    """
    Traverse a nested dictionary by path.
    """
    for item in path:
      obj = obj.get(item, None)
      if not obj:
        return None
    return obj

if __name__ == '__main__':
  # Process all .docx files in ./doc/ and output chunks as JSON
  listFileFolderDoc = Path("./doc/").glob("*.docx")
  for file in listFileFolderDoc:
    print(f"Processing {file.name}")
    s = StructExtract(
      path=file,
      title=file.name,
    )
    with open(f'./data/{file.stem}.json', 'w', encoding='utf-8') as f:
      f.write(json.dumps(s.chunks, ensure_ascii=False, indent=2))
