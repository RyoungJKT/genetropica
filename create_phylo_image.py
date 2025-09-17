"""
Create a simple phylogenetic tree placeholder image.
Run this once to generate assets/phylo_placeholder.png
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_phylo_placeholder():
    """Create a placeholder phylogenetic tree image."""
    
    # Create assets directory if it doesn't exist
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create image with white background
    width, height = 600, 400
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw tree structure with lines
    # Main branch
    draw.line([(50, 200), (200, 200)], fill='#333333', width=2)
    
    # Split into main branches
    branches = [
        [(200, 200), (350, 100), "DENV-1"],
        [(200, 200), (350, 167), "DENV-2"],
        [(200, 200), (350, 233), "DENV-3"],
        [(200, 200), (350, 300), "DENV-4"]
    ]
    
    # Colors for each serotype (matching your palette)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for i, (start, end, label) in enumerate(branches):
        # Draw branch line
        draw.line([start, end], fill='#666666', width=2)
        
        # Draw sub-branches
        sub_branches = [
            (end[0], end[1] - 20),
            (end[0], end[1]),
            (end[0], end[1] + 20)
        ]
        
        for sub_end in sub_branches[::2]:  # Draw alternating sub-branches
            draw.line([end, (end[0] + 80, sub_end[1])], fill='#999999', width=1)
            # Terminal node
            draw.ellipse([end[0] + 78, sub_end[1] - 4, end[0] + 86, sub_end[1] + 4], 
                        fill=colors[i], outline='#666666')
        
        # Draw main node
        draw.ellipse([end[0] - 5, end[1] - 5, end[0] + 5, end[1] + 5], 
                     fill=colors[i], outline='#333333')
        
        # Add label
        try:
            # Try to use a better font if available
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((end[0] + 100, end[1] - 10), label, fill='#333333', font=font)
    
    # Add title
    draw.text((width // 2 - 100, 30), "Phylogenetic Tree", fill='#333333', font=font)
    draw.text((width // 2 - 80, 50), "(Placeholder)", fill='#666666', font=font)
    
    # Add scale bar
    draw.line([(50, 350), (150, 350)], fill='#333333', width=2)
    draw.text((75, 360), "0.01 subs/site", fill='#666666', font=font)
    
    # Save image
    output_path = assets_dir / "phylo_placeholder.png"
    img.save(output_path)
    print(f"Created placeholder image at: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_phylo_placeholder()
    print("Phylogenetic placeholder image created successfully!")