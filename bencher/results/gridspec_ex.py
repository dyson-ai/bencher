import panel as pn
import numpy as np
import matplotlib.pyplot as plt


# Generating sample images
def generate_image():
    return np.random.rand(100, 100)


images = [generate_image() for _ in range(4)]

# Creating the Panel
gspec = pn.GridSpec()

# Adding images to the grid
for i in range(2):
    for j in range(2):
        plot = plt.figure(figsize=(2,2))
        plt.imshow(images[i * 2 + j], cmap="viridis", aspect="equal")
        plt.axis("off")  # Turn off axis
        gspec[i, j] = pn.pane.Matplotlib(plot)

# Adding labels for each row and column
row_labels = ["Row 1", "Row 2"]
col_labels = ["Col 1", "Col 2"]

# Adjusting row label width by setting column width
# gspec[:, 2] = pn.layout.HSpacer(width=50)  # Setting the width of the third column

label_row = pn.Column()
for i, label in enumerate(row_labels):
    # gspec[i, 2] = pn.panel(label, align='center')
    pt = pn.panel(label, align="center")
    label_row.append(pt)
    # pt.param["width"].readonly=True
    # pt.param["height"].readonly=True

    # gspec[i, 2] = pt

label_col = pn.Row()

for j, label in enumerate(col_labels):
    pt = pn.panel(
        label,
        align="center",
        # height=1,
    )
    # pt.param["width"].readonly = True
    # pt.param["height"].readonly = True
    label_col.append(pt)

    # gspec[2, j] = pt

# Adding an empty cell at the bottom-right corner
# gspec[2, 2] = pn.Spacer()
outer_outer = pn.Column()
outer = pn.Row()
outer.append(label_row)
outer.append(gspec)
outer_outer.append(outer)
label_row._update_manual()
print(label_row.width)
label_col.insert(0,pn.layout.Spacer(width=100))
outer_outer.append(label_col)

outer_outer.show()

# outer_g = pn.GridSpec()
# outer_g[0:1,0] = label_row
# outer_g[0,:] = label_col
# outer_g[1,1] = gspec

# print(outer_g)
# outer_g.show()
