from steve import Component

body_x = Component("body_x", name="Surge actuator body")
body_x.box("body", 180, 46, 46, at=(90, 0, 0))
body_x.cylinder("bore", 10, 200, at=(-12, 0, 0), direction=(1, 0, 0), op="cut")
body_x.material("aluminum-6061-t6", color="#c5cad1")

