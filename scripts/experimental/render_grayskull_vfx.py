import sys
import os
import math
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
output_path = "frontend/public/vfx/grayskull_lightning_vfx.webm"

WIDTH, HEIGHT = 540, 960
FPS = 60
TOTAL_FRAMES = 168 # ~2.8 seconds

# Card dimensions inside the canvas
CARD_LEFT, CARD_RIGHT = 70, 470
CARD_TOP, CARD_BOTTOM = 400, 890
TOP_CENTER = ((CARD_LEFT + CARD_RIGHT) // 2, CARD_TOP)

# Fractal lightning generation
def generate_lightning_path(start, end, jitter_scale=15.0, min_segment=10):
    points = [start, end]
    curr_jitter = jitter_scale
    while True:
        new_points = [points[0]]
        divided = False
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if dist > min_segment:
                divided = True
                mid_x = (p1[0] + p2[0]) / 2.0
                mid_y = (p1[1] + p2[1]) / 2.0
                # Perpendicular displacement
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                nx = -dy / dist
                ny = dx / dist
                disp = (random.random() - 0.5) * 2.0 * curr_jitter
                new_points.append((mid_x + nx * disp, mid_y + ny * disp))
            new_points.append(p2)
        points = new_points
        curr_jitter *= 0.6
        if not divided:
            break
    return points

# Spark particles
sparks = []
for _ in range(80):
    sparks.append({
        'x': random.uniform(CARD_LEFT, CARD_RIGHT),
        'y': random.uniform(CARD_TOP, CARD_BOTTOM),
        'vx': random.uniform(-4, 4),
        'vy': random.uniform(-6, -1),
        'size': random.uniform(1.5, 4.0),
        'life': random.uniform(0.2, 1.0),
        'age': random.uniform(0, 1.0),
        'color': random.choice([(0, 243, 255), (255, 255, 255), (120, 220, 255)])
    })

print(f"Iniciando render de {TOTAL_FRAMES} frames para Rayo Grayskull...")

# Prepare ffmpeg process
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

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

for f in range(TOTAL_FRAMES):
    t = f / FPS # Current time in seconds
    
    # Create empty RGBA frame
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. FASE 1 & 2: Arcos trepando por los bordes (0s -> 1.05s, frames 0 -> 63)
    if f < 75:
        # Progress of climbing (0.0 to 1.0)
        progress = min(1.0, f / 48.0)
        top_progress = max(0.0, min(1.0, (f - 35) / 25.0))
        
        # Left edge lightning: (CARD_LEFT, CARD_BOTTOM) -> (CARD_LEFT, CARD_TOP)
        curr_left_y = CARD_BOTTOM - (CARD_BOTTOM - CARD_TOP) * progress
        p_left = generate_lightning_path((CARD_LEFT, CARD_BOTTOM), (CARD_LEFT, curr_left_y), jitter_scale=12.0)
        
        # Right edge lightning: (CARD_RIGHT, CARD_BOTTOM) -> (CARD_RIGHT, CARD_TOP)
        curr_right_y = CARD_BOTTOM - (CARD_BOTTOM - CARD_TOP) * progress
        p_right = generate_lightning_path((CARD_RIGHT, CARD_BOTTOM), (CARD_RIGHT, curr_right_y), jitter_scale=12.0)
        
        # Draw glows on left and right
        for p in [p_left, p_right]:
            # Outer cyan glow
            draw.line(p, fill=(0, 243, 255, 160), width=9)
            # Mid bright glow
            draw.line(p, fill=(150, 245, 255, 220), width=5)
            # Inner white core
            draw.line(p, fill=(255, 255, 255, 255), width=2)
            
        # Top edges moving to center: (CARD_LEFT, CARD_TOP) -> TOP_CENTER and (CARD_RIGHT, CARD_TOP) -> TOP_CENTER
        if top_progress > 0:
            curr_top_left_x = CARD_LEFT + (TOP_CENTER[0] - CARD_LEFT) * top_progress
            p_top_l = generate_lightning_path((CARD_LEFT, CARD_TOP), (curr_top_left_x, CARD_TOP), jitter_scale=8.0)
            
            curr_top_right_x = CARD_RIGHT - (CARD_RIGHT - TOP_CENTER[0]) * top_progress
            p_top_r = generate_lightning_path((CARD_RIGHT, CARD_TOP), (curr_top_right_x, CARD_TOP), jitter_scale=8.0)
            
            for p in [p_top_l, p_top_r]:
                draw.line(p, fill=(0, 243, 255, 180), width=9)
                draw.line(p, fill=(150, 245, 255, 230), width=5)
                draw.line(p, fill=(255, 255, 255, 255), width=2)
                
    # 2. FASE 3: COLISIÓN EN LA CÚSPIDE + MEGARRAYO AL CIELO (Frames 58 -> 155, ~0.95s -> 2.6s)
    if f >= 58 and f <= 155:
        climax_f = f - 58
        intensity = 1.0
        if f > 130:
            intensity = max(0.0, (155 - f) / 25.0)
            
        # A. Onda de Choque Expansiva desde la Cúspide
        if climax_f < 35:
            shock_r = climax_f * 7.5 + 10
            shock_alpha = int(255 * (1.0 - climax_f / 35.0) * intensity)
            draw.ellipse(
                [TOP_CENTER[0] - shock_r, TOP_CENTER[1] - shock_r,
                 TOP_CENTER[0] + shock_r, TOP_CENTER[1] + shock_r],
                outline=(0, 243, 255, shock_alpha),
                width=int(4 * (1.0 - climax_f / 35.0) + 1)
            )
            
        # B. Destello Anamórfico Horizontal (Lens Flare Streak)
        flare_w = int(240 * intensity + random.uniform(-20, 20))
        flare_h = int(6 * intensity)
        draw.ellipse(
            [TOP_CENTER[0] - flare_w, TOP_CENTER[1] - flare_h,
             TOP_CENTER[0] + flare_w, TOP_CENTER[1] + flare_h],
            fill=(0, 243, 255, int(190 * intensity))
        )
        draw.ellipse(
            [TOP_CENTER[0] - flare_w//2, TOP_CENTER[1] - flare_h//2,
             TOP_CENTER[0] + flare_w//2, TOP_CENTER[1] + flare_h//2],
            fill=(255, 255, 255, int(255 * intensity))
        )
        
        # C. Megarrayo Vertical de Plasma hacia el Cielo
        # Main vertical column from TOP_CENTER[1] to y = 0
        beam_w_outer = int(random.uniform(50, 75) * intensity)
        beam_w_mid = int(random.uniform(22, 34) * intensity)
        beam_w_core = int(random.uniform(8, 14) * intensity)
        
        # Outer blue-cyan plasma aura
        draw.rectangle([TOP_CENTER[0] - beam_w_outer, 0, TOP_CENTER[0] + beam_w_outer, TOP_CENTER[1]], fill=(0, 180, 255, int(110 * intensity)))
        # Mid bright plasma
        draw.rectangle([TOP_CENTER[0] - beam_w_mid, 0, TOP_CENTER[0] + beam_w_mid, TOP_CENTER[1]], fill=(0, 243, 255, int(180 * intensity)))
        # Core pure white incandescent beam
        draw.rectangle([TOP_CENTER[0] - beam_w_core, 0, TOP_CENTER[0] + beam_w_core, TOP_CENTER[1]], fill=(255, 255, 255, int(255 * intensity)))
        
        # Dynamic electric tendrils dancing inside the beam
        for _ in range(4):
            branch_start = (TOP_CENTER[0] + random.uniform(-10, 10), random.uniform(TOP_CENTER[1] * 0.1, TOP_CENTER[1]))
            branch_end = (branch_start[0] + random.uniform(-65, 65), branch_start[1] - random.uniform(80, 180))
            branch_p = generate_lightning_path(branch_start, branch_end, jitter_scale=16.0)
            draw.line(branch_p, fill=(0, 243, 255, int(180 * intensity)), width=4)
            draw.line(branch_p, fill=(255, 255, 255, int(240 * intensity)), width=1)
            
        # Top Sky Explosion Orb
        sky_r = int(random.uniform(70, 110) * intensity)
        draw.ellipse([-sky_r + TOP_CENTER[0], -sky_r, sky_r + TOP_CENTER[0], sky_r], fill=(0, 243, 255, int(150 * intensity)))
        draw.ellipse([-sky_r//2 + TOP_CENTER[0], -sky_r//2, sky_r//2 + TOP_CENTER[0], sky_r//2], fill=(255, 255, 255, int(220 * intensity)))
        
        # Central Power Sword Orb on vertex
        core_r = int(random.uniform(22, 38) * intensity)
        draw.ellipse([TOP_CENTER[0] - core_r, TOP_CENTER[1] - core_r, TOP_CENTER[0] + core_r, TOP_CENTER[1] + core_r], fill=(0, 243, 255, int(200 * intensity)))
        draw.ellipse([TOP_CENTER[0] - core_r//2, TOP_CENTER[1] - core_r//2, TOP_CENTER[0] + core_r//2, TOP_CENTER[1] + core_r//2], fill=(255, 255, 255, int(255 * intensity)))
        
    # 3. SPARK PARTICLES (Active across the whole animation)
    for sp in sparks:
        if f > 20 and f < 155:
            sp['x'] += sp['vx'] + random.uniform(-1, 1)
            sp['y'] += sp['vy']
            sp['age'] += 1.0 / (sp['life'] * FPS)
            if sp['age'] >= 1.0 or sp['y'] < 0:
                sp['x'] = random.uniform(CARD_LEFT - 20, CARD_RIGHT + 20)
                sp['y'] = random.uniform(CARD_TOP - 10, CARD_BOTTOM)
                sp['age'] = 0.0
                
            alpha = int(255 * math.sin(sp['age'] * math.pi))
            sr = sp['size']
            col = (*sp['color'], alpha)
            draw.ellipse([sp['x'] - sr, sp['y'] - sr, sp['x'] + sr, sp['y'] + sr], fill=col)

    # 4. HDR Glow Pass with Gaussian Blur Filter
    # Create soft blur glow image and merge
    glow_img = img.filter(ImageFilter.GaussianBlur(radius=5.0))
    glow_img2 = img.filter(ImageFilter.GaussianBlur(radius=15.0))
    
    # Composite: glow2 + glow + sharp image
    final_frame = Image.alpha_composite(Image.alpha_composite(glow_img2, glow_img), img)
    
    # Convert to bytes and send to ffmpeg pipe
    raw_data = final_frame.tobytes()
    proc.stdin.write(raw_data)

proc.stdin.close()
proc.wait()
print(f"✅ Rayo Grayskull VFX generado con éxito en: {output_path}")
