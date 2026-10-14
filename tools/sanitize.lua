-- Pandoc filter for the site build. Raw HTML from Markdown is shown as text, not
-- markup, and link or image targets with an active scheme are neutralised. Pages
-- are built from pull-request content, so neither may reach the browser as code.

local function as_text(s)
  return pandoc.Str(s)
end

-- Browsers strip ASCII control characters and whitespace from a URL before reading its
-- scheme, so "java&#x0A;script:" is "javascript:" to them. Normalise the same way before
-- checking, and allow only schemes that cannot run script.
local ALLOWED_SCHEMES = { http = true, https = true, mailto = true }

local function is_safe(url)
  local normalised = url:gsub("[%c%s]", ""):lower()
  local scheme = normalised:match("^([%a][%w+.-]*):")
  return scheme == nil or ALLOWED_SCHEMES[scheme] == true
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
  if not is_safe(el.target) then
    el.target = "#"
  end
  return el
end

function Image(el)
  if not is_safe(el.src) then
    el.src = ""
  end
  return el
end
