from PIL import Image, ImageDraw

def create_assets():
    apple = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(apple)
    draw.ellipse([2, 2, 18, 18], fill="red", outline="darkred")
    apple.save("apple.png")

    head = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(head)
    draw.rectangle([0, 0, 20, 20], fill="green")
    draw.ellipse([4, 4, 8, 8], fill="white")
    draw.ellipse([12, 4, 16, 8], fill="white")
    head.save("head.png")

    body = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(body)
    draw.rectangle([2, 2, 18, 18], fill="lime", outline="green")
    body.save("body.png")

    print("Aset berhasil dibuat: apple.png, head.png, body.png")

if __name__ == "__main__":
    create_assets()