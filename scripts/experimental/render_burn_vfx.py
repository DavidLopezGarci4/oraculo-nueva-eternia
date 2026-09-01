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

WIDTH, HEIGHT = 540, 960
FPS = 60
TOTAL_FRAMES = 168 # ~2.8 seconds

# Card dimensions matching the lightning overlay
CARD_LEFT, CARD_RIGHT = 70, 470
CARD_TOP, CARD_BOTTOM = 400, 890
CARD_WIDTH = CARD_RIGHT - CARD_LEFT
CARD_HEIGHT = CARD_BOTTOM - CARD_TOP

# Ash & Ember particle system
random.seed(42)
particles = []
for _ in range(160):
    spawn_y_ratio = random.uniform(0.0, 1.0)
    particles.append({
        'x': random.uniform(CARD_LEFT - 25, CARD_RIGHT + 25),
        'y_ratio': spawn_y_ratio,
        'vx': random.uniform(-2.5, 2.5),
        'vy': random.uniform(-4.5, -1.8),
        'size': random.uniform(1.5, 4.5),
        'life': random.uniform(0.6, 1.4),
        'active': False,
        'age': 0.0,
        'is_ember': random.random() > 0.45,
        'color': random.choice([
            (255, 230, 120),
            (255, 140, 30),
            (255, 70, 10),
            (160, 150, 150),
            (100, 90, 90)
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
    "-b:v", "3M",
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
    
    burn_norm = max(0.0, min(1.0, (f - 15) / 95.0))
    curr_burn_y = CARD_TOP + CARD_HEIGHT * burn_norm
    
    # 1. LLAMAS VIVAS EN LA LÍNEA DE COMBUSTIÓN
    if f >= 8 and f <= 128:
        flame_intensity = math.sin(min(1.0, (f - 8) / 25.0) * math.pi * 0.5)
        if f > 105:
            flame_intensity = max(0.0, (128 - f) / 23.0)
            
        tongue_count = 28
        step_x = CARD_WIDTH / tongue_count
        
        for i in range(tongue_count + 1):
            base_x = CARD_LEFT + i * step_x + random.uniform(-6, 6)
            base_y = curr_burn_y + random.uniform(-4, 6)
            flame_h = random.uniform(25, 65) * flame_intensity
            tip_x = base_x + random.uniform(-14, 14) + math.sin(f * 0.3 + i) * 8
            tip_y = base_y - flame_h
            
            draw.polygon([
                (base_x - 14, base_y),
                (tip_x, tip_y),
                (base_x + 14, base_y)
            ], fill=(240, 60, 10, int(190 * flame_intensity)))
            
            draw.polygon([
                (base_x - 8, base_y),
                (tip_x * 0.8 + base_x * 0.2, tip_y + 10),
                (base_x + 8, base_y)
            ], fill=(255, 150, 20, int(220 * flame_intensity)))
            
            draw.polygon([
                (base_x - 4, base_y),
                (tip_x * 0.5 + base_x * 0.5, tip_y + 22),
                (base_x + 4, base_y)
            ], fill=(255, 245, 160, int(255 * flame_intensity)))
            
        beam_h = random.uniform(8, 16)
        draw.rectangle(
            [CARD_LEFT - 15, curr_burn_y - beam_h, CARD_RIGHT + 15, curr_burn_y + beam_h],
            fill=(255, 120, 20, int(170 * flame_intensity))
        )
        draw.rectangle(
            [CARD_LEFT - 5, curr_burn_y - beam_h*0.4, CARD_RIGHT + 5, curr_burn_y + beam_h*0.4],
            fill=(255, 235, 160, int(240 * flame_intensity))
        )

    # 2. PARTICULAS DE CENIZA Y ASCUAS
    for p in particles:
        if not p['active'] and burn_norm >= p['y_ratio'] and f >= 15:
            p['active'] = True
            p['current_x'] = p['x']
            p['current_y'] = CARD_TOP + CARD_HEIGHT * p['y_ratio'] + random.uniform(-10, 10)
            p['age'] = 0.0

        if p['active']:
            p['age'] += 1.0 / (p['life'] * FPS)
            if p['age'] < 1.0:
                wind_x = math.sin(f * 0.15 + p['x']) * 1.6
                p['current_x'] += p['vx'] + wind_x
                p['current_y'] += p['vy']
                
                alpha = int(255 * math.sin(p['age'] * math.pi) * (1.0 - p['age'] * 0.4))
                sz = p['size'] * (1.0 - p['age'] * 0.5)
                
                if p['is_ember']:
                    draw.ellipse(
                        [p['current_x'] - sz, p['current_y'] - sz, p['current_x'] + sz, p['current_y'] + sz],
                        fill=(*p['color'], alpha)
                    )
                    draw.ellipse(
                        [p['current_x'] - sz*2, p['current_y'] - sz*2, p['current_x'] + sz*2, p['current_y'] + sz*2],
                        fill=(*p['color'], int(alpha * 0.35))
                    )
                else:
                    draw.polygon([
                        (p['current_x'] - sz, p['current_y']),
                        (p['current_x'] + sz * 0.5, p['current_y'] - sz),
                        (p['current_x'] + sz, p['current_y'] + sz * 0.5),
                        (p['current_x'] - sz * 0.5, p['current_y'] + sz)
                    ], fill=(*p['color'], int(alpha * 0.8)))
            else:
                p['active'] = False

    # 3. GLOW PASS & COMPOSITE
    glow1 = img.filter(ImageFilter.GaussianBlur(radius=4.0))
    glow2 = img.filter(ImageFilter.GaussianBlur(radius=12.0))
    
    final_frame = Image.alpha_composite(Image.alpha_composite(glow2, glow1), img)
    raw_data = final_frame.tobytes()
    proc.stdin.write(raw_data)

proc.stdin.close()
proc.wait()
print(f"Completado con exito: {output_path}")
