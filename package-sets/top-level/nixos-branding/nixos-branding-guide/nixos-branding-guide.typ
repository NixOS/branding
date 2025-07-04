// Date must be set to none for deterministic builds
#set document(date: none)
#set page("a4", flipped: true)
#set text(font: "Route 159")

#let color_palette = toml("colors/colors.toml")
#let version = read("data/version")

#let sectionTitle(content, size: 36pt) = {
  upper(text(size: size, weight: "bold", content))
}

#let sectionPage(content, text_size: 36pt) = {
  page(margin: (x: 0pt, y: 0pt), layout(size => {
    let text_content = sectionTitle(size: text_size)[#content]
    let text_size = measure(text_content)
    let text_start = 5 / 9 * size.height - text_size.height / 2
    if (counter(page).get().at(0) == 1) {
      place(
        top + left,
        dx: 1.1cm,
        dy: text_start + text_size.height + 1em,
      )[#text(size: 1.2em, weight: "bold", font: "Jura")[VERSION #version]]
    }
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
    context [
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
      #let page_num = if here().page() < 10 {
        [0#str(here().page())]
      } else {
        here().page()
      };
      #place(bottom + right, dx: -2.5em, dy: -2.5em, [
        #text(fill: white, weight: 900, font: "Jura", [#page_num])
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

#let lambda_prime = [#sym.lambda#sym.prime]

#sectionPage[NixOS Branding Guide]

#align(center + horizon)[#text(size: 1.2em)[
    #set par(justify: true)
    #layout(size => {
      rect(
        width: 54% * size.width,
        stroke: none,
        [
          We believe in open-source innovation and a community-driven ethos — values that have shaped our identity from the very beginning.
          As you explore this guide, we hope you’ll sense the spirit of stable evolution — a core principle we embrace over stagnation or chaos.

          This guide serves as a framework to help ensure that our communication and design consistently reflect the values that define Nix: innovation, reliability, and simplicity.
          It brings together creative expression and technical precision to foster a unified identity across all touchpoints.

          We’ve aimed to include everything you need to feel confident and comfortable when working with the NixOS visual identity — the public face of our declarative builds and deployments ecosystem.
          If anything is unclear or you have questions, we’re always happy to help.

          Please feel free to reach out to the Marketing Team or the Brand and Design Steward directly.
          You can find contact information here:
          #link(
            "https://nixos.org/community/teams/marketing",
          )[nixos.org/community/teams/marketing]
        ],
      )
    })

  ]
]

#contentPage(
  leftSide: (
    content: [
      #grid(columns: 1fr, align: center, [
          #text(size: 36pt, weight: "bold")[INDEX]
        ])
    ],
    header: none,
  ),
  rightSide: (
    content: text(weight: "bold")[
      IDENTITY \
      LOGO \
      TYPOGRAPHY \
      COLOR
    ],
    header: (),
  ),
)

#sectionPage[Identity]

#align(center + horizon)[#text(size: 1.2em)[
    #set par(justify: true)
    #layout(size => {
      rect(
        width: 54% * size.width,
        stroke: none,
        [
          Design is not just surface-level — it is a reflection of who we are.
          Our visual identity — the NixOS snowflake with its two shades of blue, clean geometry, and recursive form — signals the values we share.

          #text(weight: "bold")[
            Openness

            Transparency

            Inclusivity
          ]

          These brand guidelines are not rigid constraints, but clear and thoughtful principles designed to guide consistent, intentional expression.
          They reflect the maturity of our community and help us communicate with consistency and intention.
          They also help prevent confusion with other ecosystems and reinforce the unique identity of NixOS.

          A cohesive brand builds confidence — not just in the project, but in the people behind it.
          It creates alignment around a shared vision and helps express the distinctive spirit of the open source community we are proud to be part of.

          We hope you feel that same sense of pride and belonging.
          This is more than a project — it is a movement shaped by all of us.
        ],
      )
    })

  ]
]

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
      - `thickness`: The distance from the lambda skeleton to the vertices.
        It follows lines angled at multiples of 60°.
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
      All meaningful dimensions of the lambda emerge as simply rational numbers given the default values of `thickness` and `gap` and setting the `radius` to `1 / 2` such that the hexagon maximal diameter is `1`.
      In all cases, the denominator is a power of `2`.
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
      All angles are integer multiples of 60°. \
      `A` angles are 60°. \
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
      The first end point references the vertices of the lambda with zero gap.
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
      If the inner hexagon maximal diameter is 1, the outer hexagon maximal diameter is 9 / 4.
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
      The proportions of the logotype are driven by the height of the "N" glyph.
      The "i" glyph has been mirrored along the vertical axis.
      No other modifications have been made to the glyphs.
      The glyphs have been manually kerned to maintain a balance between simplicity and identity.
    ],
    header: ("Anatomy", "Logotype"),
  ),
)

#contentPage(
  leftSide: (
    content: image("./dimensioned/nixos-logo-dimensioned.svg"),
    header: none,
  ),
  rightSide: (
    content: [
      When combining the logomark and logotype, the dimensions of the logotype are driven by the dimensions of the logomark.
      A line intersecting the forward heel and upper notch of upper left and bottom right lambdas intersects the top and bottom of the "N" glyph.
      The exact mathematical formula for the height of the "N" glyph is $ sqrt(3) "radius" (1 + 2 "thickness"). $
      The spacing between the logomark and logotype is manually set and displayed as the fraction of the height of the "N" glyph.
    ],
    header: ("Anatomy", "Logo"),
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

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: 1fr, rows: (
          1fr,
          1fr,
          1fr,
          1fr,
          1fr,
        ), gutter: 3em, align: center, [], [
          #box(
            stroke: (
              top: (paint: black, dash: "dashed"),
              bottom: (paint: black, dash: "dashed"),
            ),
            width: 100%,
            image(
              "./internal/nixos-logo-default-gradient-black-regular-horizontal-none.svg",
              height: 80%,
            ),
          )
        ],
        [
          #box(
            stroke: (
              top: (paint: black, dash: "dashed"),
              bottom: (paint: black, dash: "dashed"),
            ),
            width: 100%,
            image(
              "./internal/nixos-logomark-default-gradient-none.svg",
              height: 80%,
            ),
          )],
        [
          #box(
            stroke: (
              top: (paint: black, dash: "dashed"),
              bottom: (paint: black, dash: "dashed"),
            ),
            width: 100%,
            image(
              "./internal/nixos-logotype-black-regular-none.svg",
              height: 80%,
            ),
          )
        ]
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      The minimum size for the logo, logomark, and logotype is defined by their height.

      #strong([Digital]) 24 px \
      #strong([Print]) 6 mm or 0.24 in
    ],
    header: ("Sizing",),
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
          Black/#lambda_prime

          #imageBox(image(
            "./media-kit/nixos-logotype-black-lambdaprime-recommended.svg",
          ))
        ],
        [
          White/#lambda_prime

          #imageBoxDark(image(
            "./media-kit/nixos-logotype-white-lambdaprime-recommended.svg",
          ))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      There are two color style variants of the logotype: #strong([normal]) and #strong([#lambda_prime (lambda prime)]).

      The #lambda_prime variant shades the "x" in #strong([NixOS]) using the default colors of the logomark, drawing attention to the lambda shape embedded within the letter — a visual homage to our roots in functional programming.
      This symbol holds special meaning for the project, representing our alignment with functional principles and the elegance they bring to software design.

      For situations where a more neutral or subdued appearance is appropriate, the normal variant provides a clean, consistent option suitable for all contexts.

      #strong([Note]): The #lambda_prime variant must not be used in combination with the logomark.
    ],
    header: ("Variations", "Logotype", "Styles"),
  ),
)


#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr, 1fr),
        rows: 1fr,
        gutter: 1em,
        align: center,
        [
          Do not crop the logo or any of its components.

          #imageBox(image("./misuse/nixos-logo-misuse-crop.svg", height: 75%))
        ],
        [
          Do not independently scale logo components.

          #imageBox(image("./misuse/nixos-logo-misuse-scale.svg", height: 75%))
        ],

        [
          Do not use the #lambda_prime variant with the logomark.

          #imageBox(image(
            "./misuse/nixos-logo-misuse-lambdaprime.svg",
            height: 75%,
          ))
        ],
        [
          Do not distort the logo or any of its components.

          #imageBox(
            skew(
              ax: -10deg,
              image(
                "./media-kit/nixos-logo-default-gradient-black-regular-horizontal-minimal.svg",
                height: 75%,
              ),
            ),
          )
        ],

        [
          Do not mirror or flip the logo or any of its components.

          #imageBox(image(
            "./misuse/nixos-logomark-misuse-mirror.svg",
            height: 75%,
          ))
        ],
        [
          Do not rotate the logo or any of its components.

          #imageBox(image(
            "./misuse/nixos-logomark-misuse-rotate.svg",
            height: 75%,
          ))
        ],

        [
          Do not use the logo on similarly-colored backgrounds.

          #imageBox(
            fill: blue.transparentize(50%),
            stroke: none,
            image(
              "./media-kit/nixos-logo-default-gradient-black-regular-horizontal-minimal.svg",
              height: 75%,
            ),
          )
        ],
        [
          Do not place the logo on a cake.

          #imageBox(image("images/cake.svg", height: 75%))
          #place(center + horizon, dy: -7%, scale(y: 85%, image(
            "./internal/nixos-logomark-default-gradient-none.svg",
            height: 16%,
          )))
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      The NixOS logo is a key element of our visual identity.
      To preserve its integrity and recognizability, it must be used with care.
      Distorting, excessively cropping, or altering the logo can compromise its clarity and risk confusion with other software ecosystems — something we actively seek to avoid.

      Always ensure the logo has sufficient clear space.
      When uncertain, err on the side of generosity; a few extra pixels can help maintain legibility and visual impact.
    ],
    header: ("Misuse",),
  ),
)


#sectionPage[Typography]

#let route159_text = (
  "AaBbCcDdEeFfGgHhIiJjKkLlMm",
  "NnOoPpQqRrSsTtUuVvWwXxYyZz",
  "0123456789.,;:!?()[]{}–—‘’“”",
  "@#&%*/\+-=_~^$€£¥±≠≤≥∞",
)

#let route159_text_alt = (
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  "abcdefghijklmnopqrstuvwxyz",
  "0123456789.,;:!?()[]{}–—‘’“”",
  "@#&%*/\+-=_~^$€£¥±≠≤≥∞",
)

#contentPage(
  leftSide: (
    content: [
      #set par(justify: true)
      #text(size: 4.75em)[
        #route159_text.join("").split("").join(sym.zws)
      ]
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      The NixOS typeface is Route 159, a modern sans serif designed for clarity and digital readability.
      Originally developed by #link("https://dotcolon.net/")[dotcolon] as a web font, Route 159 draws on the experience behind the Vegur and Aileron typefaces, with a strong emphasis on screen performance.

      The design balances precision and approachability, making it well-suited for the NixOS logotype.
      Route 159 helps reinforce the NixOS identity: clean, efficient, and thoughtfully engineered.
    ],
    header: ("Logo Typeface", "Route 159"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: 2,
        rows: (18em,) + (1fr,) * 3,
        align: top,
        column-gutter: 3em,
        text(size: 20em)[Aa], [],
        text(size: 1.6em, weight: "regular")[
          #route159_text_alt.join("\n")
        ],
        text(size: 1.6em, weight: "regular")[
          Regular
        ],

        text(size: 1.6em, weight: "light")[
          #route159_text_alt.join("\n")
        ],
        text(size: 1.6em, weight: "light")[
          Light
        ],

        text(size: 1.6em, weight: "bold")[
          #route159_text_alt.join("\n")
        ],
        text(size: 1.6em, weight: "bold")[
          Bold
        ],
      )
    ],
    header: none,
    inset: true,
  ),
  rightSide: (
    content: [
      #strong([Regular]) is the standard weight used in the NixOS logotype and across most brand applications.
      It strikes a balance between readability and presence.

      #strong([Light]) offers a softer tone and may be used alongside the logo in contexts where subtlety is important — such as team names, sub-branding, or secondary identifiers.

      #strong([Bold]) provides additional emphasis when needed, though it is currently reserved for future use as the identity system evolves.

      Each weight maintains the clarity, legibility, and modern character that define the Route 159 typeface.
      Their consistent use helps ensure a cohesive visual voice across NixOS communications.
    ],
    header: ("Logo Typeface", "Route 159", "Weights"),
  ),
)

#sectionPage[Color]

#let title-case(string) = {
  return string.replace(regex("[A-Za-z]+('[A-Za-z]+)?"), word => (
    upper(word.text.first()) + lower(word.text.slice(1))
  ))
}

#let make_color_block(
  text_size: 1em,
  text_enable: true,
  color_name: none,
  text_color_value_enable: true,
  color,
) = {
  let mcolor = oklch(color.at(0) * 100%, color.at(1), color.at(2) * 1deg)
  let text_color = if color.at(0) >= 0.5 { black } else { white }
  let text_color_name = if color_name == none { [] } else { color_name }
  let text_color_value = if text_color_value_enable [
    HEX: #repr(mcolor.rgb().to-hex()).replace("\"", "") \
    CMYK: #mcolor.cmyk().components().map(float).map(x => { 100 * x }).map(x => calc.round(digits: 0, x)).map(int).map(str).join(" ") \
    OKLCH: #color.at(0) #color.at(1) #color.at(2) \
  ] else { }
  let text_content = if text_enable {
    place(bottom, text(text_size, text_color)[
      #text_color_name \
      #text_color_value
    ])
  } else { }
  rect(width: 100%, height: 100%, fill: mcolor, text_content)
}

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 5,
        rows: (1fr,) * 2,
        gutter: 4pt,
        ..array
          .zip(..(
            color_palette.palette.primary,
            color_palette.palette.secondary,
            color_palette.palette.accent,
          )
            .join()
            .chunks(2))
          .join()
          .map(color => make_color_block(
            text_color_value_enable: false,
            color_name: color.name,
            color.value,
          ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      The palette is designed to balance clarity with character, blending technical precision with a sense of openness and trust.
      Our palette is divided into three main categories:

      #strong([Primary]) \
      This includes #color_palette.palette.primary.map(color => title-case(color.name)).join(last: " and ", ", ").

      #strong([Secondary]) \
      This includes #color_palette.palette.secondary.map(color => title-case(color.name)).join(last: " and ", ", ").

      #strong([Accent]) \
      This includes #color_palette.palette.accent.map(color => title-case(color.name)).join(last: " and ", ", ").

      These colors are more than visual accents—they symbolize the elegance of declarative systems and the strength of the Nix community.
      Their consistent use reinforces a unified and exquisite identity across all communication and visual touchpoints.
    ],
    header: ("Palette",),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 1,
        rows: (1fr,) * 2,
        ..color_palette.palette.primary.map(color => make_color_block(
          text_size: 1em,
          color_name: color.name,
          color.value,
        ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      #color_palette.palette.primary.map(color => title-case(color.name)).join(last: " and ", ", ") form the foundation of our visual system.
      They provide the structural balance needed to support other colors and ensure accessibility and clarity across all mediums.
      Use them for text, backgrounds, borders, and general layout scaffolding.
      Their neutrality allows the other colors in the palette to shine while maintaining a clean, professional tone.
    ],
    header: ("Palette", "Primary"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 1,
        rows: (1fr,) * 2,
        ..color_palette.palette.secondary.map(color => make_color_block(
          text_size: 1em,
          color_name: color.name,
          color.value,
        ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      #color_palette.palette.secondary.map(color => title-case(color.name)).join(last: " and ", ", ") are the signature colors of the NixOS brand.
      These shades are used for prominent elements such as headers, icons, navigation bars, and key interface components.
      They evoke trust, stability, and clarity — perfectly aligned with the principles of declarative design.
      When in doubt, reach for these blues.
    ],
    header: ("Palette", "Secondary"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 3,
        rows: (1fr,) * 2,
        gutter: 4pt,
        ..array
          .zip(..(
            color_palette.palette.accent,
          )
            .join()
            .chunks(2))
          .join()
          .map(color => make_color_block(
            text_size: 1em,
            color_name: color.name,
            color.value,
          ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      #color_palette.palette.accent.map(color => title-case(color.name)).join(last: " and ", ", ") bring vibrancy and dimension to the brand.
      These colors are intended for subtle emphasis: buttons, charts, tags, illustrations, and other moments of interaction or expression.
      Use them intentionally — sparingly, but confidently — to enhance communication without overwhelming the design.
    ],
    header: ("Palette", "Accent"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 9,
        rows: 1fr,
        ..(
          color_palette.palette.primary.at(0).tints.pairs(),
          color_palette.palette.secondary.map(x => x.tints.pairs()).join(),
          color_palette.palette.accent.map(x => x.tints.pairs()).join(),
        )
          .join()
          .map(color => make_color_block(
            text_size: 0.45em,
            color_name: color.at(0),
            color.at(1),
          ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      Tints provide a flexible extension of the core palette, offering a wide range of lightness levels—from subtle backgrounds to bold accents.
      These variations are useful for layering, accessibility, and adapting to different themes or environments.

      While tints increase design versatility, they are intended to complement, not replace, the primary, secondary, and accent colors.
      Use them thoughtfully to maintain brand consistency and visual harmony.
    ],
    header: ("Palette", "Tints"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 1,
        rows: (1fr,) * 2,
        ..color_palette.logos.default.map(color => make_color_block(
          text_size: 1em,
          color_name: color.name,
          color.value,
        ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      The NixOS logo uses two carefully selected color values derived from the core palette:

      - A tint of Afghani Blue with a lightness of 0.55 and chroma 0.12
      - A customized tint of Argentinian Blue with a lightness of 0.75 and a slightly reduced chroma of 0.09

      While the Afghani Blue tint follows the standard palette, the Argentinian Blue variant has been subtly adjusted.
      The chroma was reduced from 0.12 (as defined in the palette) to 0.09 to better align with the historic appearance of the NixOS logo in earlier versions and maintain visual continuity with its established identity.

      These two tones work together to preserve the logo’s familiar character while adapting it to a more precise and accessible color system based on OKLCH.
    ],
    header: ("Logo", "Default"),
  ),
)

#contentPage(
  leftSide: (
    content: [
      #grid(
        columns: (1fr,) * 1,
        rows: (1fr,) * 6,
        ..color_palette.logos.rainbow.map(color => make_color_block(
          text_size: 1em,
          color.value,
        ))
      )
    ],
    header: none,
  ),
  rightSide: (
    content: [
      The rainbow variant of the NixOS logo features six colors inspired by the traditional rainbow Pride flag.
      These colors have been carefully adapted to better align with the visual language of the NixOS brand — they are softer and less saturated than the original flag, allowing them to integrate more seamlessly with the logomark’s geometry and tone.

      This kind of adaptation is a common practice among organizations seeking to balance symbolic representation with brand cohesion.
      The result is a respectful and visually consistent expression of solidarity with the LGBTQ+ community.

      The rainbow variant is used to celebrate diversity, inclusion, and the vibrant community that shapes NixOS.
    ],
    header: ("Logo", "Rainbow"),
  ),
)
