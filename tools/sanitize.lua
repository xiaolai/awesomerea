-- Pandoc filter for the site build. Raw HTML from Markdown is shown as text, not
-- markup, and link or image targets with an active scheme are neutralised. Pages
-- are built from pull-request content, so neither may reach the browser as code.

local function as_text(s)
  return pandoc.Str(s)
end

local function is_active(url)
  local scheme = url:match("^%s*([%a][%w+.-]*):")
  if not scheme then return false end
  scheme = scheme:lower()
  return scheme == "javascript" or scheme == "vbscript" or scheme == "data"
end

function RawInline(el)
  if el.format:lower():match("html") then
    return as_text(el.text)
  end
end

function RawBlock(el)
  if el.format:lower():match("html") then
    return pandoc.Para({ as_text(el.text) })
  end
end

function Link(el)
  if is_active(el.target) then
    el.target = "#"
  end
  return el
end

function Image(el)
  if is_active(el.src) then
    el.src = ""
  end
  return el
end
