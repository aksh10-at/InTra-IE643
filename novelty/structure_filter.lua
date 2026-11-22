-- Document structure clean-up for the reconstructed PDFs (novelty/structure.py).
-- Changes only markup and layout, never words:
--   * a paragraph that is only a short bold phrase ("**Update rule:**") becomes a level-4
--     label heading, so the writer's sub-labels look the same everywhere
--   * a trailing colon is dropped from headings ("Recap:" -> "Recap")
--   * every heading asks for room below it, so it never sits alone at the bottom of a page
--   * a short "Label:" line directly above a list becomes a label heading (the list itself is
--     recognised because structure.py turns on pandoc's lists_without_preceding_blankline)
--   * a bold label on its own line above an equation is split off as a label heading
--   * a figure is laid out with the drawing on the left and its caption beside it on the right
--     (textbook style), which halves the height of most figures and removes large white gaps
--   * a figure description with no crop (the renderer prints "*[Diagram: ...]*") becomes a
--     marked note box instead of loose italic text

local MAX_LABEL_WORDS = 8

local function strip_colon(inlines)
  local last = inlines[#inlines]
  if last and last.t == "Str" and last.text:match(":$") and #last.text > 1 then
    inlines[#inlines] = pandoc.Str(last.text:gsub(":$", ""))
  elseif last and last.t == "Str" and last.text == ":" then
    inlines:remove(#inlines)
  end
  while #inlines > 0 and (inlines[#inlines].t == "Space" or inlines[#inlines].t == "SoftBreak") do
    inlines:remove(#inlines)
  end
  return inlines
end

local function word_count(inlines)
  local n = 0
  for _, x in ipairs(inlines) do
    if x.t == "Str" then n = n + 1 end
    if x.t == "Math" then return 99 end -- a phrase with maths is a sentence, not a label
  end
  return n
end

local function room(lines)
  return pandoc.RawBlock("latex", "\\Needspace{" .. lines .. "\\baselineskip}")
end

function Header(h)
  h.content = strip_colon(h.content)
  local need = h.level <= 1 and 8 or 6
  return { room(need), h }
end

function Para(p)
  local c = p.content
  -- *[Diagram: ...]*  ->  note box
  if #c == 1 and c[1].t == "Emph" then
    local text = pandoc.utils.stringify(c[1])
    if text:match("^%[Diagram:") then
      local inner = c[1].content
      -- drop the leading "[Diagram:" and the closing "]"
      local body = pandoc.utils.stringify(inner):gsub("^%[Diagram:%s*", ""):gsub("%]%s*$", "")
      local desc = pandoc.read(body, "markdown").blocks
      local lead = pandoc.Strong({ pandoc.Str("Drawing"), pandoc.Space(), pandoc.Str("not"), pandoc.Space(),
                                   pandoc.Str("extracted:") })
      local first = { lead, pandoc.Space() }
      if desc[1] and desc[1].content then
        for _, x in ipairs(desc[1].content) do table.insert(first, x) end
      end
      return pandoc.BlockQuote({ pandoc.Para(first) })
    end
  end
  -- **Short label**  ->  label heading (alone, or on its own line above more text)
  if c[1] and c[1].t == "Strong" and word_count(c[1].content) <= MAX_LABEL_WORDS
      and (#c == 1 or c[2].t == "SoftBreak" or c[2].t == "LineBreak") then
    local first = pandoc.utils.stringify(c[1].content)
    if not first:match("^%(?%w%)") and not first:match("^%(%w+%)") then -- "(i) ..." steps stay text
      local out = Header(pandoc.Header(4, c[1].content))
      if #c > 2 then
        local rest = pandoc.Inlines({})
        for k = 3, #c do rest:insert(c[k]) end
        table.insert(out, pandoc.Para(rest))
      end
      return out
    end
  end
  return nil
end

local function plain_label(inlines)
  local text = pandoc.utils.stringify(inlines)
  return word_count(inlines) <= 6 and text:match("^%u") and text:match(":$")
end

-- "Upcoming:" directly above a list -> label heading
function Blocks(blocks)
  local out = pandoc.Blocks({})
  for i, b in ipairs(blocks) do
    local nxt = blocks[i + 1]
    if b.t == "Para" and nxt and (nxt.t == "BulletList" or nxt.t == "OrderedList") and plain_label(b.content) then
      for _, x in ipairs(Header(pandoc.Header(4, b.content))) do out:insert(x) end
    else
      out:insert(b)
    end
  end
  return out
end

-- Figure: drawing on the left, caption on the right, both in one non-floating figure.
local function latex(inlines)
  return pandoc.write(pandoc.Pandoc({ pandoc.Plain(inlines) }), "latex")
end

function Figure(fig)
  local img = nil
  pandoc.walk_block(pandoc.Div(fig.content), { Image = function(i) img = i end })
  if not img then return nil end
  if img.src:match("^sources/") then return nil end -- original page scans stay full width
  local pct = tonumber((img.attributes["width"] or "50"):match("[%d.]+")) or 50
  local w = math.min(pct, 52) / 100
  if w < 0.25 then w = 0.25 end
  local cap = {}
  if fig.caption and fig.caption.long and fig.caption.long[1] then
    cap = fig.caption.long[1].content
  end
  local tex = "\\begin{figure}[H]\n\\begin{minipage}[c]{" .. string.format("%.3f", w) .. "\\linewidth}\\centering\n" ..
    "\\includegraphics[width=\\linewidth,height=0.24\\textheight,keepaspectratio]{" .. img.src .. "}\n" ..
    "\\end{minipage}\\hfill\n\\begin{minipage}[c]{" .. string.format("%.3f", 0.96 - w) .. "\\linewidth}\n" ..
    "\\captionsetup{justification=raggedright,singlelinecheck=false,width=\\linewidth}\n" ..
    "\\caption{" .. latex(cap) .. "}\n\\end{minipage}\n\\end{figure}"
  return pandoc.RawBlock("latex", tex)
end
