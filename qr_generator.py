import qrcode

def generate_qr(batch_id):

    url = f"http://localhost:5173/index.html?batch={batch_id}"

    img = qrcode.make(url)

    img.save(f"{batch_id}.png")

generate_qr("BATCH101")
generate_qr("BATCH102")
generate_qr("BATCH103")