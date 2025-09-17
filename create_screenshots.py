"""
Create placeholder screenshots for README documentation.
Run this once to generate screenshot images in docs/screenshots/
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_placeholder_screenshots():
    """Create three placeholder screenshots for the README."""
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path(__file__).parent / "docs" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Common settings
    width, height = 1200, 800
    
    # Try to use default font
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        label_font = ImageFont.truetype("arial.ttf", 16)
    except:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    # 1. Map View Screenshot
    img_map = Image.new('RGB', (width, height), '#FFFFFF')
    draw_map = ImageDraw.Draw(img_map)
    
    # Header
    draw_map.rectangle([(0, 0), (width, 80)], fill='#F8F9FA')
    draw_map.text((50, 30), "🦟 GeneTropica — Dengue · Climate · Forecast (MVP)", fill='#2C3E50', font=title_font)
    
    # Sidebar
    draw_map.rectangle([(0, 80), (250, height)], fill='#F5F5F5')
    draw_map.text((20, 100), "🔍 Filters", fill='#2C3E50', font=label_font)
    draw_map.text((20, 140), "Year Range: 2017-2025", fill='#666666', font=label_font)
    draw_map.text((20, 170), "Provinces: 6 selected", fill='#666666', font=label_font)
    draw_map.text((20, 200), "Serotypes: All", fill='#666666', font=label_font)
    
    # Map area (simplified Indonesia shape)
    map_area = [(300, 150), (1100, 650)]
    draw_map.rectangle(map_area, fill='#E8F4F8', outline='#CCCCCC')
    
    # Draw province bubbles with colors
    provinces = [
        (500, 300, '#FF6B6B', 'DKI'),
        (550, 320, '#4ECDC4', 'JABAR'),
        (600, 350, '#45B7D1', 'JATENG'),
        (700, 380, '#96CEB4', 'JATIM'),
        (480, 330, '#FF6B6B', 'BANTEN'),
        (620, 380, '#4ECDC4', 'DIY')
    ]
    
    for x, y, color, name in provinces:
        draw_map.ellipse([x-30, y-30, x+30, y+30], fill=color, outline='white', width=2)
        draw_map.text((x+40, y-10), name, fill='#333333', font=label_font)
    
    # Legend
    legend_y = 250
    for i, (serotype, color) in enumerate([('DENV1', '#FF6B6B'), ('DENV2', '#4ECDC4'), 
                                           ('DENV3', '#45B7D1'), ('DENV4', '#96CEB4')]):
        draw_map.ellipse([1120, legend_y + i*40, 1140, legend_y + 20 + i*40], fill=color)
        draw_map.text((1150, legend_y + 5 + i*40), serotype, fill='#333333', font=label_font)
    
    # Month slider
    draw_map.rectangle([(300, 700), (1100, 720)], fill='#E0E0E0')
    draw_map.ellipse([900, 695, 930, 725], fill='#667EEA')
    draw_map.text((500, 730), "November 2024", fill='#333333', font=label_font)
    
    img_map.save(screenshots_dir / "map_view.png")
    
    # 2. Trends View Screenshot
    img_trends = Image.new('RGB', (width, height), '#FFFFFF')
    draw_trends = ImageDraw.Draw(img_trends)
    
    # Header
    draw_trends.rectangle([(0, 0), (width, 80)], fill='#F8F9FA')
    draw_trends.text((50, 30), "📈 Trends & Climate Analysis", fill='#2C3E50', font=title_font)
    
    # Left chart - Stacked area
    draw_trends.rectangle([(50, 120), (580, 450)], outline='#E0E0E0', width=1)
    draw_trends.text((250, 140), "Serotype Composition Over Time", fill='#333333', font=label_font)
    
    # Draw stacked areas (simplified)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    y_positions = [400, 350, 280, 200]
    for i, (y, color) in enumerate(zip(y_positions, colors)):
        points = [(100, 450), (100, y), (200, y-20), (300, y+10), (400, y-15), (500, y), (530, y), (530, 450)]
        draw_trends.polygon(points, fill=color)
    
    # Right chart - Dual axis
    draw_trends.rectangle([(620, 120), (1150, 450)], outline='#E0E0E0', width=1)
    draw_trends.text((800, 140), "Cases vs Climate Variables", fill='#333333', font=label_font)
    
    # Draw bars for cases
    bar_heights = [250, 280, 220, 300, 270, 240]
    for i, h in enumerate(bar_heights):
        x = 650 + i * 80
        draw_trends.rectangle([(x, 450-h), (x+50, 450)], fill='#636EFA', outline='#636EFA')
    
    # Draw line for rainfall
    rain_points = [(675, 300), (755, 280), (835, 320), (915, 260), (995, 290), (1075, 310)]
    for i in range(len(rain_points)-1):
        draw_trends.line([rain_points[i], rain_points[i+1]], fill='#00CED1', width=2)
    
    # Correlation text
    draw_trends.text((650, 480), "💧 Rainfall (lag 2mo): -0.485", fill='#666666', font=label_font)
    draw_trends.text((850, 480), "🌡️ Temperature: 0.232", fill='#666666', font=label_font)
    
    img_trends.save(screenshots_dir / "trends_view.png")
    
    # 3. Forecast View Screenshot
    img_forecast = Image.new('RGB', (width, height), '#FFFFFF')
    draw_forecast = ImageDraw.Draw(img_forecast)
    
    # Header
    draw_forecast.rectangle([(0, 0), (width, 80)], fill='#F8F9FA')
    draw_forecast.text((50, 30), "📊 Forecast (Prototype)", fill='#2C3E50', font=title_font)
    
    # Warning box
    draw_forecast.rectangle([(100, 120), (1100, 180)], fill='#FFF3CD', outline='#FFC107')
    draw_forecast.text((120, 140), "⚠️ Educational Prototype - Not for clinical decision-making", fill='#856404', font=label_font)
    
    # Forecast chart area
    draw_forecast.rectangle([(100, 220), (1100, 600)], outline='#E0E0E0', width=1)
    
    # Historical line (blue)
    historical = [(150, 450), (250, 420), (350, 480), (450, 400), (550, 430), (650, 410), (750, 450)]
    for i in range(len(historical)-1):
        draw_forecast.line([historical[i], historical[i+1]], fill='#2E86AB', width=3)
        draw_forecast.ellipse([historical[i][0]-4, historical[i][1]-4, 
                               historical[i][0]+4, historical[i][1]+4], fill='#2E86AB')
    
    # Forecast line (purple dashed)
    forecast_points = [(750, 450), (850, 470), (950, 460)]
    for i in range(len(forecast_points)-1):
        # Draw dashed line
        x1, y1 = forecast_points[i]
        x2, y2 = forecast_points[i+1]
        for j in range(0, int(abs(x2-x1)), 10):
            if j % 20 < 10:
                draw_forecast.line([(x1+j, y1), (x1+j+5, y1)], fill='#A23B72', width=2)
    
    # Confidence interval (shaded area)
    draw_forecast.polygon([(750, 430), (850, 440), (950, 430), (950, 490), (850, 500), (750, 470)],
                          fill='#F0E6F0', outline=None)
    
    # Metrics boxes
    metrics = [
        ("MAE (Backtest)", "152.3 cases"),
        ("RMSE (Backtest)", "198.7 cases"),
        ("Backtest Samples", "12 months")
    ]
    
    for i, (label, value) in enumerate(metrics):
        x = 150 + i * 300
        draw_forecast.rectangle([(x, 640), (x+250, 720)], fill='#F8F9FA', outline='#E0E0E0')
        draw_forecast.text((x+20, 660), label, fill='#666666', font=label_font)
        draw_forecast.text((x+20, 685), value, fill='#2C3E50', font=title_font)
    
    img_forecast.save(screenshots_dir / "forecast_view.png")
    
    print("✅ Created 3 placeholder screenshots:")
    print(f"  - {screenshots_dir}/map_view.png")
    print(f"  - {screenshots_dir}/trends_view.png")
    print(f"  - {screenshots_dir}/forecast_view.png")
    
    return screenshots_dir

if __name__ == "__main__":
    create_placeholder_screenshots()
    print("\nScreenshots created successfully!")
    print("These are placeholder images. Replace with actual screenshots before production.")