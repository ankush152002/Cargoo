from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def visualize_3d(container_dimensions, shipments):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot container edges
    r = [0, container_dimensions['length']]
    X, Y = np.meshgrid(r, r)
    Z = np.array([[0, 0], [container_dimensions['height'], container_dimensions['height']]])
    ax.plot_surface(X, Y, Z, color='blue', alpha=0.1)
    ax.plot_surface(X, Y, np.zeros_like(X), color='blue', alpha=0.1)
    ax.plot_surface(X, Y, np.full_like(X, container_dimensions['height']), color='blue', alpha=0.1)
    ax.plot_surface(X, np.zeros_like(Y), Z, color='blue', alpha=0.1)
    ax.plot_surface(X, np.full_like(Y, container_dimensions['width']), Z, color='blue', alpha=0.1)

    # Plot shipments
    cmap = plt.cm.get_cmap('tab20', len(shipments))  # Get a colormap with enough distinct colors
    for i, shipment in enumerate(shipments):
        x = shipment.get('x', 0)
        y = shipment.get('y', 0)
        z = shipment.get('z', 0)
        length = shipment.get('length', 1)
        width = shipment.get('width', 1)
        height = shipment.get('height', 1)

        # Define vertices for the shipment box
        vertices = [
            [x, y, z],
            [x + length, y, z],
            [x + length, y + width, z],
            [x, y + width, z],
            [x, y, z + height],
            [x + length, y, z + height],
            [x + length, y + width, z + height],
            [x, y + width, z + height]
        ]

        # Create the faces of the box
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[3], vertices[0], vertices[4], vertices[7]],
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]]
        ]

        # Plot the shipment box
        poly3d = Poly3DCollection(faces, facecolors=cmap(i), linewidths=1, edgecolors='r', alpha=.5)
        ax.add_collection3d(poly3d)

        # Label each shipment
        ax.text(x + length / 2, y + width / 2, z + height / 2, f'Shipment {shipment["id"]}', color='black', ha='center', va='center')

    # Set limits and remove labels
    ax.set_xlim(0, container_dimensions['length'])
    ax.set_ylim(0, container_dimensions['width'])
    ax.set_zlim(0, container_dimensions['height'])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    plt.show()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)

        # Validate columns
        required_columns = ['container_length', 'container_width', 'container_height', 'id', 'x', 'y', 'z', 'length', 'width', 'height']
        if not all(col in df.columns for col in required_columns):
            return 'Error: CSV file is missing one or more required columns.'

        # Assuming the CSV file contains the necessary columns
        container_dimensions = {
            'length': df['container_length'].iloc[0],
            'width': df['container_width'].iloc[0],
            'height': df['container_height'].iloc[0]
        }

        shipments = df[['id', 'x', 'y', 'z', 'length', 'width', 'height']].to_dict('records')

        visualize_3d(container_dimensions, shipments)
        return 'File uploaded and visualization complete'
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
