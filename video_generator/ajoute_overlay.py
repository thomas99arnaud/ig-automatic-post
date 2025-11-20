import re
import numpy as np
import path
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\Windows\Fonts\impact.ttf"   # vérifie que ce fichier existe

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def render_sentence_image(
    sentence,
    text_color_hex,
    max_width_px,
    font_size=52,
    pad_x=24,
    pad_y=20,
):
    """
    Rend une phrase dans une image (fond blanc arrondi + contour + texte centré),
    retourne un np.array RGBA.
    """
    font = ImageFont.truetype(FONT_PATH, font_size)

    # 1) Wrap manuel pour ne pas dépasser max_width_px
    # On construit les lignes à partir des mots
    tmp_img = Image.new("RGBA", (max_width_px, 2000), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp_img)

    words = sentence.split(" ")
    lines = []
    current_line = ""
    for w in words:
        test_line = (current_line + " " + w).strip()
        bbox = tmp_draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] > max_width_px:  # trop large, on valide la ligne précédente
            if current_line:
                lines.append(current_line)
            current_line = w
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    wrapped_text = "\n".join(lines)

    # 2) Mesurer le bloc de texte complet
    line_spacing = int(font_size * 0.25)
    bbox = tmp_draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=font,
        spacing=line_spacing,
        align="left",
    )
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 3) Taille finale de la box blanche
    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2

    # 4) Créer l'image finale
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fond blanc arrondi + contour noir
    radius = 30
    draw.rounded_rectangle(
        (0, 0, box_w - 1, box_h - 1),
        radius=radius,
        fill=(255, 255, 255, 230),
        width=4,
    )

    # 5) Dessiner le texte centré dans la box
    text_color = hex_to_rgb(text_color_hex)
    # on centre le bloc de texte dans la box (padding uniforme)
    text_x = (box_w - text_w) // 2
    text_y = (box_h - text_h) // 2

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font,
        fill=text_color + (255,),
        spacing=line_spacing,
        align="center",
    )

    return np.array(img)


def add_subtitles_colorful_animated(
    SUJET,
    text: str,
):

    video_path = path.TEMPORARY_VIDEOS_PATH / f"{SUJET}_full.mp4"
    video = VideoFileClip(video_path)

    # Découper le texte en phrases
    sentences = re.split(r'(?<=[\.\!\?…])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    total_duration = video.duration
    seg_duration = total_duration / len(sentences)

    clips = []

    # Palette de couleurs pour le texte
    colors = ["#FFD60A", "#FF6B6B", "#4ECDC4", "#A66CFF", "#00B4D8"]

    # Position verticale (~ 20% de la hauteur)
    top_y = int(video.h * 0.20)
    max_text_width = int(video.w * 0.8)

    for i, sentence in enumerate(sentences):
        start = i * seg_duration
        end = start + seg_duration
        text_color_hex = colors[i % len(colors)]

        img_array = render_sentence_image(
            sentence,
            text_color_hex=text_color_hex,
            max_width_px=max_text_width,
            font_size=52,
            pad_x=24,
            pad_y=20,
        )

        txt_clip = (
            ImageClip(img_array)
            .with_start(start)
            .with_end(end)
            .with_position(("center", top_y))
        )

        clips.append(txt_clip)

    final = CompositeVideoClip([video, *clips])
    out_path = path.VIDEOS_EDITED_PATH / f"{SUJET}.mp4"
    final.write_videofile(out_path, codec="libx264", audio_codec="aac")
    print("Vidéo avec le son et les sous titres ✅")
    return out_path


if __name__ == "__main__":
    text = "Tu savais que ton chat peut reconnaître son prénom ? Mais il choisit souvent de l'ignorer… parce que c’est un boss ! Alors, respecte le pouvoir du roi des câlins !"

    reel_with_color = add_subtitles_colorful_animated(
        "reel_chat_final.mp4",
        text,
        out_path="reel_chat_caption_color.mp4",
    )

    print("🏁 Reel final coloré + font stylée :", reel_with_color)
