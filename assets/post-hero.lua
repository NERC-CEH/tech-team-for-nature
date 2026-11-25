-- Story, news and diary pages: show the post's card image (its `image:`) as a wide photo at the top.
-- Turn it off for one post with `hero: false` (e.g. when the photo is already in the text).
local function esc(s) return (s:gsub('[&<>"]', { ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;", ['"'] = "&quot;" })) end

function Pandoc(doc)
  local m = doc.meta
  if not m.image or m.listing or m.hero == false then return doc end
  local src = pandoc.utils.stringify(m.image)
  if src == "" or src:match("^%a+:") or src:match("^/") then return doc end
  local alt = m["image-alt"] and pandoc.utils.stringify(m["image-alt"]) or ""
  table.insert(doc.blocks, 1, pandoc.RawBlock("html",
    '<figure class="post-hero"><img src="' .. esc(src) .. '" alt="' .. esc(alt) .. '"></figure>'))
  return doc
end
