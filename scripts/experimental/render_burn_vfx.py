import sys
import os
import math
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs("frontend/public/vfx", exist_ok=True)
output_path = "frontend/public/vfx/grayskull_burn_vfx.webm"

WIDTH, HEIGHT = 600, 800
FPS = 60
TOTAL_FRAMES = 168 # ~2.8 seconds

# Card dimensions matching the exact 3:4 card aspect ratio
CARD_LEFT, CARD_RIGHT = 0, 600
CARD_TOP, CARD_BOTTOM = 0, 800
CARD_WIDTH = CARD_RIGHT - CARD_LEFT
CARD_HEIGHT = CARD_BOTTOM - CARD_TOP

# Ash & Ember particle system
random.seed(42)
particles = []
for _ in range(220):
    spawn_y_ratio = random.uniform(0.0, 1.0)
    particles.append({
        'x': random.uniform(-20, CARD_WIDTH + 20),
        'y_ratio': spawn_y_ratio,
        'vx': random.uniform(-3.0, 3.0),
        'vy': random.uniform(-5.5, -2.2),
        'size': random.uniform(2.0, 5.5),
        'life': random.uniform(0.7, 1.5),
        'active': False,
        'age': 0.0,
        'is_ember': random.random() > 0.4,
        'color': random.choice([
            (255, 240, 150),
            (255, 160, 40),
            (255, 80, 20),
            (200, 50, 10),
            (160, 150, 150),
            (110, 100, 100)
        ])
    })

print(f"Iniciando render de {TOTAL_FRAMES} frames...")

# Prepare ffmpeg process with DEVNULL for stderr to prevent pipe buffer deadlock
cmd = [
    ffmpeg_exe, "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgba",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libvpx-vp9",
    "-pix_fmt", "yuva420p",
    "-b:v", "4M",
    "-auto-alt-ref", "0",
    output_path
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for f in range(TOTAL_FRAMES):
    if f % 30 == 0 or f == TOTAL_FRAMES - 1:
        print(f"Progreso render: Frame {f+1}/{TOTAL_FRAMES} ({int((f+1)/TOTAL_FRAMES*100)}%)")
        
    t = f / FPS
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    burn_norm = max(0.0, min(1.0, (f - 10) / 100.0))
    curr_burn_y = -30 + (CARD_HEIGHT + 70) * burn_norm
    
    # 1. LLAMAS VIVAS EN LA LÍNEA DE COMBUSTIÓN (SWEPT DESDE ARRIBA HASTA ABAJO)
    if f >= 6 and f <= 135:
        flame_intensity = math.sin(min(1.0, (f - 6) / 20.0) * math.pi * 0.5)
        if f > 110:
            flame_intensity = max(0.0, (135 - f) / 25.0)
            
        tongue_count = 42
        step_x = CARD_WIDTH / tongue_count
        
        # Lenguas de fuego multinivel orgánicas
        for i in range(tongue_count + 2):
            base_x = CARD_LEFT + (i - 1) * step_x + random.uniform(-6, 6)
            base_y = curr_burn_y + random.uniform(-4, 6)
            flame_h = random.uniform(35, 90) * flame_intensity
            tip_x = base_x + random.uniform(-18, 18) + math.sin(f * 0.35 + i) * 12
            tip_y = base_y - flame_h
            
            # Capa externa: Rojo fuego profundo
            draw.polygon([
                (base_x - 18, base_y + 4),
                (tip_x, tip_y),
                (base_x + 18, base_y + 4)
            ], fill=(230, 45, 5, int(190 * flame_intensity)))
            
            # Capa intermedia: Naranja incandescente
            draw.polygon([
                (base_x - 11, base_y + 2),
                (tip_x * 0.8 + base_x * 0.2, tip_y + 12),
                (base_x + 11, base_y + 2)
            ], fill=(255, 140, 15, int(225 * flame_intensity)))
            
            # Capa interna: Núcleo blanco/dorado
            draw.polygon([
                (base_x - 5, base_y),
                (tip_x * 0.5 + base_x * 0.5, tip_y + 26),
                (base_x + 5, base_y)
            ], fill=(255, 250, 190, int(250 * flame_intensity)))
            
        # Resplandor horizontal difuso orgánico (sin bordes duros)
        for band_offset, band_alpha, band_col in [
            (14, 110, (255, 80, 10)),
            (8, 160, (255, 140, 25)),
            (3, 230, (255, 240, 180))
        ]:
            draw.line(
                [(CARD_LEFT - 10, curr_burn_y), (CARD_RIGHT + 10, curr_burn_y)],
                fill=(*band_col, int(band_alpha * flame_intensity)),
                width=int(band_offset * 2)
            )

    # 2. PARTICULAS DE CENIZA Y ASCUAS EN VUELO ASCENDENTE
    for p in particles:
        if not p['active'] and burn_norm >= p['y_ratio'] and f >= 10:
            p['active'] = True
            p['current_x'] = p['x']
            p['current_y'] = CARD_TOP + CARD_HEIGHT * p['y_ratio'] + random.uniform(-10, 10)
            p['age'] = 0.0

        if p['active']:
            p['age'] += 1.0 / (p['life'] * FPS)
            if p['age'] < 1.0:
                wind_x = math.sin(f * 0.18 + p['x']) * 2.2
                p['current_x'] += p['vx'] + wind_x
                p['current_y'] += p['vy']
                
                alpha = int(255 * math.sin(p['age'] * math.pi) * (1.0 - p['age'] * 0.35))
                sz = p['size'] * (1.0 - p['age'] * 0.45)
                
                if p['is_ember']:
                    draw.ellipse(
                        [p['current_x'] - sz, p['current_y'] - sz, p['current_x'] + sz, p['current_y'] + sz],
                        fill=(*p['color'], alpha)
                    )
                    draw.ellipse(
                        [p['current_x'] - sz*2, p['current_y'] - sz*2, p['current_x'] + sz*2, p['current_y'] + sz*2],
                        fill=(*p['color'], int(alpha * 0.4))
                    )
                else:
                    draw.polygon([
                        (p['current_x'] - sz, p['current_y']),
                        (p['current_x'] + sz * 0.5, p['current_y'] - sz),
                        (p['current_x'] + sz, p['current_y'] + sz * 0.5),
                        (p['current_x'] - sz * 0.5, p['current_y'] + sz)
                    ], fill=(*p['color'], int(alpha * 0.75)))
            else:
                p['active'] = False

    # 3. GLOW PASS & COMPOSITE
    glow1 = img.filter(ImageFilter.GaussianBlur(radius=5.0))
    glow2 = img.filter(ImageFilter.GaussianBlur(radius=14.0))
    
    final_frame = Image.alpha_composite(Image.alpha_composite(glow2, glow1), img)
    raw_data = final_frame.tobytes()
    proc.stdin.write(raw_data)

proc.stdin.close()
proc.wait()

# Copiar también al directorio de distribución dist si existe
dist_vfx = "frontend/dist/vfx/grayskull_burn_vfx.webm"
if os.path.exists("frontend/dist/vfx"):
    import shutil
    shutil.copyfile(output_path, dist_vfx)

print(f"Completado con exito: {output_path}")
