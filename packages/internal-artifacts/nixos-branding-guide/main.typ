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
  Anatomy - Lambda - Annotations
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-annotated-vertices.svg")
][
  The lambda is created by referencing the geometry of a hexagon.
  The lambda skeleton intersects the hexagon vertices at three locations:
  - At the top left between the upper apex and upper notch.
  - At the bottom left at the rear foot.
  - At the bottom right between the forward heel and the forward tip.
]

#contentPage[
  Anatomy - Lambda - Parameters
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-annotated-parameters.svg")
][
  The lambda is defined by three parameters:

  - `radius`: The distance from the origin to the vertex intersection points.
  - `thickness`: The distance from the lambda skeleton to the edge.
    This can be observed in the 6 lines forming a triangle beneath the origin.
    It is defined as a fraction of the `radius` with a default value of `1 / 4`.
  - `gap`: This distance that the upper apex and upper notch are translated towards the origin.
    The dashed section is the lambda with no gap.
    It is defined as a fraction of the `radius` with a default value of `1 / 32`.
]

#contentPage[
  Anatomy - Lambda - Linear
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-linear.svg")
][
  All meaningful dimensions of the lambda emerge as simply rational numbers given the default values of `thickness` and `radius` and setting the `radius` to 2 such that the hexagon maximal diameter is 1.
  In all cases, the denominator is a power of 2.
]

#contentPage[
  Anatomy - Lambda - Angular
][
  #image("./dimensioned-images/nixos-lambda-dimensioned-angular.svg")
][
  All angles are integer multiples of 60°.
  `A` angles are 60°.
  `B` angles are 120°.
]

#contentPage[
  Anatomy - Gradient - Definition
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-gradient-annotated.svg")
][
  The gradient of the lambda is defined by 2 points.
  The first end point is located at the intersection above the upper notch and to the left of the upper apex.
  The second end point is located to the right of the joint crotch coincident with the lambda skeleton.

  The gradient stop points are located at 0%, 25%, and 100%.
]

#contentPage[
  Anatomy - Gradient - Unmasked
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-gradient-background.svg")
][
  The selected color of the lambda is true below and to the right of the 100% gradient stop point.
  The lightness and chroma is lowered at the 25% and 0% gradient stop points.
]

#contentPage[
  Anatomy - Logomark
][
  #image("./dimensioned-images/nixos-logomark-dimensioned-linear.svg")
][
  Six lambdas are used to create the "NixOS Snowflake".
  The lambdas are located using an inner hexagon.
  They are located such that if they had zero gap, the upper apex would be coincident with a vertex of the inner hexagon and the long diagonal of the lambda is colinear with an edge of the lambda.
  An outer hexagon emerges with vertices that are coincident with the rear foot of the lambdas.
  If the maximal diameter of the inner hexagon is 1 the outer hexagon emerges with maximal diameter of 9 / 4.
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
][ ][
  #lorem(100)
]

#contentPage[
  Clearspace - Logomark
][ ][
  #lorem(100)
]

#contentPage[
  Clearspace - Logotype
][ ][
  #lorem(100)
]

#contentPage[
  Sizing
][ ][
  #lorem(100)
]

#contentPage[
  Variations
][ ][
  #lorem(100)
]

#contentPage[
  Misuse
][ ][
  #lorem(100)
]

#sectionPage[Typography]

#sectionPage[Color]
