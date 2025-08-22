import os
import argparse
from PIL import Image
from resizeimage import resizeimage


def resize_images(input_folder, output_folder, size):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Add other formats if needed
            try:
                # Open the image file
                with open(os.path.join(input_folder, filename), 'r+b') as fd_img:
                    img = Image.open(fd_img)
                    # Resize the image
                    img = resizeimage.resize_contain(img, size)
                    # Save the resized image in the output folder
                    img.save(os.path.join(output_folder, filename), img.format)
                    print(f"Resized and saved: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Resize images in a folder.")
    parser.add_argument("input_folder", help="Path to the input folder containing images.")
    parser.add_argument("output_folder", help="Path to the output folder to save resized images.")
    parser.add_argument("width", type=int, help="Width of the resized images.")
    parser.add_argument("height", type=int, help="Height of the resized images.")

    args = parser.parse_args()

    # Get the size tuple
    size = (args.width, args.height)

    # Resize images
    resize_images(args.input_folder, args.output_folder, size)


if __name__ == "__main__":
    main()
