#set page("a4", flipped: true)
#set text(font: "Route 159")

#let sectionTitle(content, size: 36pt) = {
  upper(text(size: size, weight: "bold", content))
}

#let sectionPage(content, text_size: 36pt) = {
  page(
    margin: (x: 1cm, y: 0pt), background: align(
      right, image("./background-images/nixos-lambda-R512-T1_4-G0-none.svg", height: 100%),
    ), layout(size => {
      let text_content = sectionTitle(size: text_size)[#content]
      let text_size = measure(text_content)
      let text_start = 5 / 9 * size.height - text_size.height / 2
      place(top + left, dy: text_start)[#text_content]
    }),
  )
}

#sectionPage[NixOS Branding Guide]
#lorem(300)

#sectionPage[Brand Identity]
#lorem(300)

#sectionPage[Logo]

= Anatomy

== Lambda (λ)
#image(
  "./dimensioned-images/nixos-lambda-dimensioned-annotated-parameters.svg",
)
#image("./dimensioned-images/nixos-lambda-dimensioned-annotated-vertices.svg")

#image("./dimensioned-images/nixos-lambda-dimensioned-linear.svg")
#image("./dimensioned-images/nixos-lambda-dimensioned-angular.svg")
