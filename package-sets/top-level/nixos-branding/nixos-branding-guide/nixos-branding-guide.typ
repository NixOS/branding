// Date must be set to none for deterministic builds
#set document(date: none)
#set page("a4", flipped: true)
#set text(font: "Route 159")

#let sectionTitle(content, size: 36pt) = {
  upper(text(size: size, weight: "bold", content))
}

#let sectionPage(content, text_size: 36pt) = {
  page(margin: (x: 0pt, y: 0pt), layout(size => {
    let text_content = sectionTitle(size: text_size)[#content]
    let text_size = measure(text_content)
    let text_start = 5 / 9 * size.height - text_size.height / 2
    [
      #place(top + left, dx: 1cm, dy: text_start)[#text_content]
      #place(top + right)[#image(
          "./miscellaneous/nixos-lambda-R512-T1_4-G0-none.svg",
        )]
    ]
  }))
}


#let contentPage(leftSide: none, rightSide: none) = {
  page(
    margin: (x: 0cm, y: 0cm),
    header: [
      #h(1fr) #rightSide.header
    ],
    [
      #grid(
        columns: (2fr, 1fr),
        rows: 1fr,
        gutter: 0em,
        grid.cell(align: horizon, box(
          inset: if leftSide.at("inset", default: false) { 2.5em } else { 0em },
          [
            #leftSide.content
          ],
        )),
        grid.cell(align: horizon, fill: black, box(inset: 2.5em)[
          #set text(fill: white)
          #rightSide.content
        ]),
      )
      #place(top + left, dx: 200% / 3 + 2.5em, dy: 2.5em, [
        #text(fill: white, weight: 900, font: "Jura", rightSide.header.join(
          " / ",
        ))
      ])
    ],
  )
}

#let imageBox(
  content,
  fill: none,
  stroke: (paint: gray, dash: "dashed", thickness: 0.5pt),
) = {
  box(fill: fill, stroke: stroke, content)
}

#let imageBoxDark(
  content,
  fill: black,
  stroke: none,
) = {
  box(fill: fill, stroke: stroke, content)
}

#sectionPage[NixOS Branding Guide]
#lorem(300)

#sectionPage[Brand Identity]
#lorem(300)

#sectionPage[Logo]

#contentPage(
  leftSide: (
    content: image(
      "./dimensioned/nixos-lambda-dimensioned-annotated-vertices.svg",
    ),
    header: none,
  ),
  rightSide: (
    content: [
      The lambda is created by referencing the geometry of a hexagon.
      The lambda skeleton intersects the hexagon vertices at three locations:
      - At the top left between the upper apex and upper notch.
      - At the bottom left at the rear foot.
      - At the bottom right between the forward heel and the forward tip.
    ],
    header: ("Anatomy", "Lambda", "Annotations"),
  ),
)

#contentPage(
  leftSide: (
    content: image(
      "./dimensioned/nixos-lambda-dimensioned-annotated-parameters.svg",
    ),
    header: none,
  ),
  rightSide: (
    content: [
      The lambda is defined by three parameters:

      - `radius`: The distance from the origin to the vertex intersection points.
      - `thickness`: The distance from the lambda skeleton to the edge.
        This can be observed in the 6 lines forming a triangle beneath the origin.
        It is defined as a fraction of the `radius` with a default value of `1 / 4`.
      - `gap`: This distance that the upper apex and upper notch are translated towards the origin.
        The dashed section is the lambda with no gap.
        It is defined as a fraction of the `radius` with a default value of `1 / 32`.
    ],
    header: ("Anatomy", "Lambda", "Parameters"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./dimensioned/nixos-lambda-dimensioned-linear.svg"),
    header: none,
  ),
  rightSide: (
    content: [
      All meaningful dimensions of the lambda emerge as simply rational numbers given the default values of `thickness` and `gap` and setting the `radius` to 2 such that the hexagon maximal diameter is 1.
      In all cases, the denominator is a power of 2.
    ],
    header: ("Anatomy", "Lambda", "Linear"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./dimensioned/nixos-lambda-dimensioned-angular.svg"),
    header: none,
  ),
  rightSide: (
    content: [
      All angles are integer multiples of 60°.
      `A` angles are 60°.
      `B` angles are 120°.
    ],
    header: ("Anatomy", "Lambda", "Angular"),
  ),
)

#contentPage(
  leftSide: (
    content: image(
      "./dimensioned/nixos-logomark-dimensioned-gradient-annotated.svg",
    ),
    header: none,
  ),
  rightSide: (
    content: [
      The gradient of the lambda is defined by 2 points.
      The first end point is located at the intersection above the upper notch and to the left of the upper apex.
      The second end point is located to the right of the joint crotch coincident with the lambda skeleton.

      The gradient stop points are located at 0%, 25%, and 100%.
    ],
    header: ("Anatomy", "Gradient", "Definition"),
  ),
)

#contentPage(
  leftSide: (
    content: image(
      "./dimensioned/nixos-logomark-dimensioned-gradient-background.svg",
    ),
    header: none,
  ),
  rightSide: (
    content: [
      The selected color of the lambda is true below and to the right of the 100% gradient stop point.
      The lightness and chroma is lowered at the 25% and 0% gradient stop points.
    ],
    header: ("Anatomy", "Gradient", "Unmasked"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./dimensioned/nixos-logomark-dimensioned-linear.svg"),
    header: none,
  ),
  rightSide: (
    content: [
      Six lambdas are used to create the "NixOS Snowflake".
      The lambdas are located using an inner hexagon.
      They are located such that if they had zero gap, the upper apex would be coincident with a vertex of the inner hexagon and the long diagonal of the lambda is colinear with an edge of the inner hexagon.
      An outer hexagon emerges with vertices that are coincident with the rear foot of the lambdas.
      If the inner hexagon maximal diameter is 1, the outer hexagon maximal diameter of 9 / 4.
    ],
    header: ("Anatomy", "Logomark"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./dimensioned/nixos-logotype-dimensioned.svg"),
    header: none,
  ),
  rightSide: (
    content: [
      #lorem(100)
    ],
    header: ("Anatomy", "Logotype"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./clearspace/nixos-logo-clearspace.svg"),
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      When placing the horizontal variant of the logo, the recommended clearspace is equivalent to the height of the logomark.
      The minimal clearspace is equivalent to half the height of the logomark.
    ],
    header: ("Clearspace", "Logo"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./clearspace/nixos-logomark-clearspace.svg"),
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      When placing the logomark, the recommended clearspace is equivalent to the height of the lambda with no gap.
      This is equivalent to half the height of the logomark.
      The minimal clearspace is equivalent to half the height of the lambda with no gap or a quarter the height of the logomark.
    ],
    header: ("Clearspace", "Logomark"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./clearspace/nixos-logotype-clearspace.svg"),
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      When placing the logotype, the recommended clearspace is equivalent to the height of the capital N in NixOS.
      The minimal clearspace is equivalent to half the height of the capital N in NixOS.
    ],
    header: ("Clearspace", "Logotype"),
  ),
)

#contentPage(leftSide: (content: none, header: none), rightSide: (
  content: lorem(100),
  header: ("Sizing",),
))

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: 1fr,
        rows: (1fr, 1fr),
        gutter: 3em,
        align: center,
        [
          Horizontal

          #imageBox(
            image(
              "./media-kit/nixos-logo-default-gradient-black-regular-horizontal-recommended.svg",
            ),
          )
        ],
        [
          Vertical

          #imageBox(
            image(
              "./media-kit/nixos-logo-default-gradient-black-regular-vertical-recommended.svg",
            ),
          )
        ]
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      Two variants of logo layout are available: horizontal and vertical.
      The horizontal layout is the primary and recommended layout.
      The vertical layout is provided as a secondary layout.
    ],
    header: ("Variations", "Logo", "Layout"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr, 1fr),
        rows: (1fr, 1fr, 1fr),
        gutter: 1em,
        align: center,
        [
          Default/Black

          #imageBox(
            image(
              "./media-kit/nixos-logo-default-gradient-black-regular-horizontal-recommended.svg",
            ),
          )
        ],
        [
          Default/White

          #imageBoxDark(
            image(
              "./media-kit/nixos-logo-default-gradient-white-regular-horizontal-recommended.svg",
            ),
          )
        ],

        [
          Rainbow/Black

          #imageBox(
            image(
              "./media-kit/nixos-logo-rainbow-gradient-black-regular-horizontal-recommended.svg",
            ),
          )
        ],
        [
          Rainbow/White

          #imageBoxDark(
            image(
              "./media-kit/nixos-logo-rainbow-gradient-white-regular-horizontal-recommended.svg",
            ),
          )
        ],

        [
          Black/Black

          #imageBox(
            image(
              "./media-kit/nixos-logo-black-flat-black-regular-horizontal-recommended.svg",
            ),
          )
        ],
        [
          White/White

          #imageBoxDark(
            image(
              "./media-kit/nixos-logo-white-flat-white-regular-horizontal-recommended.svg",
            ),
          )
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are multiple color variants of the logo.
      The colored variants of the logomark can be used with the white or black logotype.
      The black and white variants of the logomark must be used with the black and white logotypes respectively.
    ],
    header: ("Variations", "Logo", "Colors"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr, 1fr),
        rows: (1fr, 1fr),
        gutter: 1em,
        align: center,
        [
          Default/Gradient

          #imageBox(image(
            "./media-kit/nixos-logomark-default-gradient-recommended.svg",
          ))
        ],
        [
          Rainbow/Gradient

          #imageBox(image(
            "./media-kit/nixos-logomark-rainbow-gradient-recommended.svg",
          ))
        ],

        [
          Black/Flat

          #imageBox(image(
            "./media-kit/nixos-logomark-black-flat-recommended.svg",
          ))
        ],
        [
          White/Flat

          #imageBoxDark(image(
            "./media-kit/nixos-logomark-white-flat-recommended.svg",
          ))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are 4 color variants of the logomark.
      The colored variants of the logomark should use gradient colors.
      The black and white variants of the logomark must use flat colors.
    ],
    header: ("Variations", "Logomark", "Colors"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: 1fr,
        rows: (1fr, 1fr),
        gutter: 3em,
        align: center,
        [
          Gradient

          #imageBox(image(
            "./media-kit/nixos-logomark-default-gradient-recommended.svg",
          ))
        ],
        [
          Flat

          #imageBox(image(
            "./media-kit/nixos-logomark-default-flat-recommended.svg",
          ))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are 2 color styles of the logomark: gradient and flat colors.
      Generally gradient colors should be used.
      When using black or white logomarks, use flat colors.
      Flat colors can be used for any color variant when creating print or other physical media.
    ],
    header: ("Variations", "Logomark", "Color Styles"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: 1fr,
        rows: (1fr, 1fr),
        gutter: 3em,
        align: center,
        [
          Black

          #imageBox(image(
            "./media-kit/nixos-logotype-black-regular-recommended.svg",
          ))
        ],
        [
          White

          #imageBoxDark(image(
            "./media-kit/nixos-logotype-white-regular-recommended.svg",
          ))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are two color variants of the logotype: black and white.
    ],
    header: ("Variations", "Logotype", "Colors"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr, 1fr),
        rows: (1fr, 1fr),
        gutter: 1em,
        align: center,
        [
          Black/Normal

          #imageBox(image(
            "./media-kit/nixos-logotype-black-regular-recommended.svg",
          ))
        ],
        [
          White/Normal

          #imageBoxDark(image(
            "./media-kit/nixos-logotype-white-regular-recommended.svg",
          ))
        ],

        [
          Black/Colored 'X'

          #imageBox(image(
            "./media-kit/nixos-logotype-black-coloredx-recommended.svg",
          ))
        ],
        [
          White/Colored 'X'

          #imageBoxDark(image(
            "./media-kit/nixos-logotype-white-coloredx-recommended.svg",
          ))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are two color style variants of the logotype: normal and colored 'X'.
      The colored 'X' variant shades the 'x' in NixOS with the default colors of the logomark.
      The colored 'X' variant must not be used with the logomark.
    ],
    header: ("Variations", "Logotype", "Styles"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      Do not crop the logo or any of its components.

      #imageBox(image("./misuse/nixos-logo-misuse-crop.svg", height: 10%))

      Do not independently scale logo components.

      #imageBox(image("./misuse/nixos-logo-misuse-scale.svg", height: 10%))

      Do not use the ColoredX variant of the logotype with colored variants of the logomark.

      #imageBox(image("./misuse/nixos-logo-misuse-coloredx.svg", height: 10%))

      Do not mirror or flip the logo or any of its components.

      #imageBox(image("./misuse/nixos-logomark-misuse-mirror.svg", height: 10%))

      Do not rotate the logo or any of its components.

      #imageBox(image("./misuse/nixos-logomark-misuse-rotate.svg", height: 10%))
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      #lorem(100)
    ],
    header: ("Misuse",),
  ),
)


#sectionPage[Typography]

#text(size: 2em)[
  Route 159

  Primary Typeface
]

#par(leading: 0.65em * 5)[
  #text(size: 5em)[
    #(
      "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789.,;:!?()[]{}–—‘’“”@#&%*/\+-=_~^$€£¥±≠≤≥∞"
        .split("")
        .join(sym.zws)
    )
  ]
]

#sectionPage[Color]

#let generate_oklch_stops(luminance, chroma, stops) = {
  let step = 360 / (stops - 1)
  let positions = range(0, stops)
  let stops = positions.map(pos => (
    (
      oklch(luminance, chroma, pos * step * 1deg),
      pos * 100% / (stops - 1),
    )
  ))
  stops
}

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr, 1fr, 1fr, 1fr),
        rect(width: 100%, height: 100%, fill: oklch(0%, 0, 0deg)),
        rect(width: 100%, height: 100%, fill: oklch(100%, 0, 0deg)),
        rect(width: 100%, height: 100%, fill: oklch(57.74%, 0.1248, 264deg)),
        rect(width: 100%, height: 100%, fill: oklch(76.36%, 0.0866, 240deg)),
      )
    ],
    header: none,
  ),
  rightSide: (
    content: lorem(100),
    header: ("Primary Colors",),
  ),
)

#rect(width: 100%, height: 5em, fill: gradient.linear(
  space: color.oklch,
  ..generate_oklch_stops(57.74%, 0.1248, 5),
))

#rect(width: 100%, height: 5em, fill: gradient.linear(
  space: color.oklch,
  ..generate_oklch_stops(76.36%, 0.0866, 5),
))

#rect(width: 100%, height: 5em, fill: gradient
  .linear(
    (oklch(51%, 0.208963, 29.2339deg)),
    (oklch(70%, 0.204259, 43.4910deg)),
    (oklch(81%, 0.168100, 76.7800deg)),
    (oklch(60%, 0.175100, 147.560deg)),
    (oklch(60%, 0.141400, 241.380deg)),
    (oklch(46%, 0.194300, 288.710deg)),
  )
  .sharp(6))
