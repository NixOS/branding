// Date must be set to none for deterministic builds
#set document(date: none)
#set page(margin: 0pt, width: 2048pt, height: 2048pt)

#let data = json("final.json")
#let palette-colour(int) = if int == 0 { luma(0) } else if int == 1 {
  luma(255)
} else if int == 2 { rgb("#5b7ec8") } else if int == 3 {
  rgb("#87adfa")
} else if int == 4 { rgb("#5fb8f2") } else if int == 5 {
  rgb("#aaa1f6")
} else if int == 6 { rgb("#e99861") } else if int == 7 {
  rgb("#f08d94")
} else if int == 8 { rgb("#d991d2") } else if int == 9 { rgb("#6fc488") }

#let icon(
  type: none,
  colours: none,
  contents: none,
) = {
  set page(
    fill: palette-colour(if type == "standard" { colours.background } else {
      colours.border
    }),
    background: {
      if type == "standard" {
        grid(
          columns: 1,
          rows: (992pt, 64pt, 992pt),
          gutter: 0pt,
          rect(
            width: 100%,
            height: 100%,
            stroke: none,
            inset: if contents.style == "text" { 128pt } else { 0pt },
            if contents.style == "text" {
              text(
                font: "Route 159",
                weight: "bold",
                fill: palette-colour(colours.text),
                size: 800pt,
                align(center + bottom, contents.text),
              )
            } else if contents.style == "image" {
              align(center + bottom, image(
                { "icons/" + contents.image + ".svg" },
                height: 992pt,
                fit: "contain",
              ))
            } else { panic("Invalid style: " + content.style) },
          ),

          rect(width: 100%, height: 100%, fill: palette-colour(colours.border)),

          rect(
            width: 100%,
            height: 100%,
            fill: palette-colour(2),
            inset: 0pt,
            image(
              "icons/nixos-logomark-white-flat-minimal.svg",
              fit: "contain",
            ),
          ),
        )
      } else {
        circle(
          radius: 768pt,
          fill: palette-colour(colours.background),
          inset: -224pt,
          image({ "icons/" + contents.image + ".svg" }, fit: "contain"),
        )
      }
    },
  )
  pagebreak(weak: true)
  // FIXME: For some reason, the icons aren't generated correctly if there isn't *something* in the first page.
  text(fill: rgb("#00000000"), [.])
}

#if sys.inputs.singleIcon == "null" {
  for room in data.values() {
    icon(type: room.type, colours: room.colours, contents: room.contents)
  }
} else {
  icon(
    type: data.at(sys.inputs.singleIcon).type,
    colours: data.at(sys.inputs.singleIcon).colours,
    contents: data.at(sys.inputs.singleIcon).contents,
  )
}
