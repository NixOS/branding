#set page("a4", flipped: true)
#set text(font: "Route 159")

#let sectionTitle(content, size: 36pt) = {
  upper(text(size: size, weight: "bold", content))
}

#let sectionPage(content, text_size: 36pt) = {
  page(
    margin: (x: 1cm, y: 0pt),
    background: align(
      right,
      image(
        "./background-images/nixos-lambda-R512-T1_4-G0-none.svg",
        height: 100%,
      ),
    ),
    layout(size => {
      let text_content = sectionTitle(size: text_size)[#content]
      let text_size = measure(text_content)
      let text_start = 5 / 9 * size.height - text_size.height / 2
      place(top + left, dy: text_start)[#text_content]
    }),
  )
}

#let contentPage(header, leftSide, rightSide) = {
  page(
    margin: (x: 1cm, y: 1cm),
    header: [
      #h(1fr) #header
    ],
    grid(
      columns: (2fr, 1fr),
      rows: 1fr,
      gutter: 1em,
      align(horizon, leftSide), align(horizon, rightSide),
    ),
  )
}

#sectionPage[NixOS Branding Guide]
#lorem(300)

#sectionPage[Brand Identity]
#lorem(300)

#sectionPage[Logo]

#contentPage[
  Anatomy - Lambda - Parameters
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-annotated-parameters.svg")
][
  The lambda is created by referencing the geometry of a hexagon.
  The lambda skeleton intersects the top left, bottom left, and bottom right vertices of the hexagon.

  The lambda is defined by three parameters:

  - `radius`: The distance from the origin to the vertex intersection points.
  - `thickness`: A fraction of the `radius` which can be observed in the 6 lines forming a triangle beneath the origin.
  - `gap`: A fraction of the radius
]

#contentPage[
  Anatomy - Lambda - Annotations
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-annotated-vertices.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Lambda - Linear
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-linear.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Lambda - Angular
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-angular.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Gradient - Annotations
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-gradient-annotated.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Gradient - Unmasked
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-gradient-background.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Logomark
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-linear.svg")
][
  #lorem(100)
]

#contentPage[
  Anatomy - Logotype
][
  #image("./dimensioned-images/nixos-logotype-dimensioned.svg")
][
  #lorem(100)
]

#contentPage[
  Clearspace - Logo
][
][
  #lorem(100)
]

#contentPage[
  Clearspace - Logomark
][
][
  #lorem(100)
]

#contentPage[
  Clearspace - Logotype
][
][
  #lorem(100)
]

#contentPage[
  Sizing
][
][
  #lorem(100)
]

#contentPage[
  Variations
][
][
  #lorem(100)
]

#contentPage[
  Misuse
][
][
  #lorem(100)
]

#sectionPage[Typography]

#sectionPage[Color]
