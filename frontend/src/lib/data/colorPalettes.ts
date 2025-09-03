// TODO: This data has been migrated to PostgreSQL database
// Use API_ENDPOINTS.COLOR_PALETTES_DB for fetching color palette data
// This file is kept for backward compatibility and reference

export interface ColorPalette {
  skinTone: string;
  flatteringColors: {
    name: string;
    hex: string;
  }[];
  colorsToAvoid: {
    name: string;
    hex: string;
  }[];
  description: string;
}

export const colorPalettes: Record<string, ColorPalette> = {
  "Clear Winter": {
    skinTone: "Clear Winter",
    flatteringColors: [
      { name: "Hot Pink", hex: "#E3006D" },
      { name: "Cobalt Blue", hex: "#0057B8" },
      { name: "True Red", hex: "#CE0037" },
      { name: "Violet", hex: "#963CBD" },
      { name: "Emerald", hex: "#009775" },
      { name: "Ice Pink", hex: "#F395C7" },
    ],
    colorsToAvoid: [
      { name: "Muted Olive", hex: "#A3AA83" },
      { name: "Dusty Rose", hex: "#C4A4A7" },
      { name: "Terracotta", hex: "#A6631B" },
      { name: "Mustard", hex: "#B89D18" },
    ],
    description: "Clear Winter complexions look best in pure, vivid colors with blue undertones. Avoid muted, earthy tones that can make your complexion appear dull."
  },
  "Cool Winter": {
    skinTone: "Cool Winter",
    flatteringColors: [
      { name: "Emerald", hex: "#009775" },
      { name: "Cobalt Blue", hex: "#0082BA" },
      { name: "Cherry", hex: "#CE0037" },
      { name: "Sapphire", hex: "#0057B8" },
      { name: "Fuchsia", hex: "#C724B1" },
      { name: "Cool Ruby", hex: "#AA0061" },
    ],
    colorsToAvoid: [
      { name: "Orange", hex: "#FF8200" },
      { name: "Warm Gold", hex: "#F0B323" },
      { name: "Peach", hex: "#FDAA63" },
      { name: "Olive", hex: "#A09958" },
    ],
    description: "Cool Winter types look best in cool, clear colors with blue undertones. Avoid warm, earthy tones that clash with your cool complexion."
  },
  "Deep Winter": {
    skinTone: "Deep Winter",
    flatteringColors: [
      { name: "Deep Claret", hex: "#890C58" },
      { name: "Forest Green", hex: "#00594C" },
      { name: "True Red", hex: "#CE0037" },
      { name: "Navy", hex: "#002D72" },
      { name: "Amethyst", hex: "#84329B" },
      { name: "White", hex: "#FEFEFE" },
    ],
    colorsToAvoid: [
      { name: "Light Pastels", hex: "#F1EB9C" },
      { name: "Peach", hex: "#FCC89B" },
      { name: "Beige", hex: "#D3BC8D" },
      { name: "Camel", hex: "#CDA077" },
    ],
    description: "Deep Winter complexions look best in deep, rich colors with cool undertones. Avoid light pastels and warm earth tones that can wash you out."
  },
  "Soft Summer": {
    skinTone: "Soft Summer",
    flatteringColors: [
      { name: "Slate Blue", hex: "#57728B" },
      { name: "Soft Plum", hex: "#86647A" },
      { name: "Moss Green", hex: "#9CAF88" },
      { name: "Dusty Rose", hex: "#D592AA" },
      { name: "Powder Blue", hex: "#9BB8D3" },
      { name: "Mauve", hex: "#C4A4A7" },
    ],
    colorsToAvoid: [
      { name: "Bright Orange", hex: "#FF8200" },
      { name: "Bright Yellow", hex: "#FCE300" },
      { name: "Hot Pink", hex: "#E3006D" },
      { name: "Electric Blue", hex: "#00A3E1" },
    ],
    description: "Soft Summer types look best in soft, muted colors with cool undertones. Avoid bright, vivid colors that can overwhelm your delicate coloring."
  },
  "Cool Summer": {
    skinTone: "Cool Summer",
    flatteringColors: [
      { name: "Clear Blue", hex: "#0077C8" },
      { name: "Soft Fuchsia", hex: "#E31C79" },
      { name: "Cool Pink", hex: "#F395C7" },
      { name: "Lavender", hex: "#A277A6" },
      { name: "Soft Teal", hex: "#00B0B9" },
      { name: "Periwinkle", hex: "#7965B2" },
    ],
    colorsToAvoid: [
      { name: "Orange", hex: "#FF8200" },
      { name: "Warm Yellow", hex: "#FFCD00" },
      { name: "Rust", hex: "#9D4815" },
      { name: "Olive", hex: "#A09958" },
    ],
    description: "Cool Summer complexions look best in soft, cool colors with blue undertones. Avoid warm, bright colors that can clash with your cool coloring."
  },
  "Light Summer": {
    skinTone: "Light Summer",
    flatteringColors: [
      { name: "Lavender", hex: "#DD9CDF" },
      { name: "Powder Blue", hex: "#9BCBEB" },
      { name: "Dusty Rose", hex: "#ECB3CB" },
      { name: "Soft Periwinkle", hex: "#9595D2" },
      { name: "Aqua", hex: "#71C5E8" },
      { name: "Soft Pink", hex: "#F67599" },
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#131413" },
      { name: "Orange", hex: "#FF8200" },
      { name: "Bright Yellow", hex: "#FCE300" },
      { name: "Burgundy", hex: "#890C58" },
    ],
    description: "Light Summer types look best in light, soft colors with cool undertones. Avoid dark, bright, or warm colors that can overwhelm your delicate coloring."
  },
  "Clear Spring": {
    skinTone: "Clear Spring",
    flatteringColors: [
      { name: "Turquoise", hex: "#008EAA" },
      { name: "Clear Yellow", hex: "#FFCD00" },
      { name: "Bright Coral", hex: "#FF8D6D" },
      { name: "Violet", hex: "#963CBD" },
      { name: "Bright Green", hex: "#00A499" },
      { name: "Watermelon", hex: "#E40046" },
    ],
    colorsToAvoid: [
      { name: "Dusty Rose", hex: "#C4A4A7" },
      { name: "Mauve", hex: "#86647A" },
      { name: "Taupe", hex: "#A39382" },
      { name: "Muted Teal", hex: "#507F70" },
    ],
    description: "Clear Spring complexions look best in clear, bright colors with warm undertones. Avoid muted, dusty colors that can make your complexion appear dull."
  },
  "Warm Spring": {
    skinTone: "Warm Spring",
    flatteringColors: [
      { name: "Warm Beige", hex: "#FDAA63" },
      { name: "Golden Yellow", hex: "#FFB81C" },
      { name: "Apricot", hex: "#FF8F1C" },
      { name: "Coral", hex: "#FFA38B" },
      { name: "Warm Green", hex: "#74AA50" },
      { name: "Turquoise", hex: "#2DCCD3" },
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#131413" },
      { name: "Navy", hex: "#003057" },
      { name: "Cool Pink", hex: "#F395C7" },
      { name: "Burgundy", hex: "#890C58" },
    ],
    description: "Warm Spring types look best in warm, clear colors with golden undertones. Avoid cool, dark colors that can clash with your warm coloring."
  },
  "Light Spring": {
    skinTone: "Light Spring",
    flatteringColors: [
      { name: "Peach", hex: "#FCC89B" },
      { name: "Mint", hex: "#A5DFD3" },
      { name: "Coral", hex: "#FF8D6D" },
      { name: "Light Yellow", hex: "#F5E1A4" },
      { name: "Aqua", hex: "#A4DBE8" },
      { name: "Soft Pink", hex: "#FAAA8D" },
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#131413" },
      { name: "Navy", hex: "#002D72" },
      { name: "Burgundy", hex: "#890C58" },
      { name: "Dark Brown", hex: "#5C462B" },
    ],
    description: "Light Spring complexions look best in light, warm colors with yellow undertones. Avoid dark, cool colors that can overwhelm your delicate coloring."
  },
  "Soft Autumn": {
    skinTone: "Soft Autumn",
    flatteringColors: [
      { name: "Taupe", hex: "#DFD1A7" },
      { name: "Sage", hex: "#BBC592" },
      { name: "Terracotta", hex: "#C26E60" },
      { name: "Soft Teal", hex: "#487A7B" },
      { name: "Camel", hex: "#CDA788" },
      { name: "Salmon", hex: "#DB864E" },
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#131413" },
      { name: "Electric Blue", hex: "#00A3E1" },
      { name: "Hot Pink", hex: "#E3006D" },
      { name: "Bright White", hex: "#FEFEFE" },
    ],
    description: "Soft Autumn types look best in soft, warm, muted colors with golden undertones. Avoid bright, cool colors that can clash with your warm, muted coloring."
  },
  "Warm Autumn": {
    skinTone: "Warm Autumn",
    flatteringColors: [
      { name: "Mustard", hex: "#B89D18" },
      { name: "Rust", hex: "#9D4815" },
      { name: "Olive", hex: "#A09958" },
      { name: "Burnt Orange", hex: "#C4622D" },
      { name: "Teal", hex: "#00778B" },
      { name: "Forest Green", hex: "#205C40" },
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#131413" },
      { name: "Cool Pink", hex: "#F395C7" },
      { name: "Electric Blue", hex: "#00A3E1" },
      { name: "Fuchsia", hex: "#C724B1" },
    ],
    description: "Warm Autumn complexions look best in warm, rich, earthy colors with golden undertones. Avoid cool, bright colors that can clash with your warm coloring."
  },
  "Deep Autumn": {
    skinTone: "Deep Autumn",
    flatteringColors: [
      { name: "Burgundy", hex: "#890C58" },
      { name: "Chocolate", hex: "#5C462B" },
      { name: "Deep Teal", hex: "#00594C" },
      { name: "Rust", hex: "#9D4815" },
      { name: "Olive", hex: "#5E7E29" },
      { name: "Terracotta", hex: "#A6631B" },
    ],
    colorsToAvoid: [
      { name: "Pastels", hex: "#F1EB9C" },
      { name: "Light Pink", hex: "#F395C7" },
      { name: "Baby Blue", hex: "#99D6EA" },
      { name: "Mint", hex: "#A5DFD3" },
    ],
    description: "Deep Autumn types look best in deep, warm, rich colors with golden undertones. Avoid light pastels and cool colors that can wash you out."
  },

  // Monk Skin Tone Scale Data
  "Monk 1": {
    skinTone: "Monk 1 - Very Light",
    flatteringColors: [
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Alice Blue", hex: "#F0F8FF" },
      { name: "Cornsilk", hex: "#FFF8DC" },
      { name: "Beige", hex: "#F5F5DC" },
      { name: "Platinum", hex: "#E0E6E6" },
      { name: "Light Gray", hex: "#D3D3D3" },
      { name: "Light Pink", hex: "#FFB6C1" },
      { name: "Pale Green", hex: "#98FB98" },
      { name: "Sky Blue", hex: "#87CEEB" },
      { name: "Plum", hex: "#DDA0DD" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Gold", hex: "#FFD700" }
    ],
    description: "Your very light skin tone pairs beautifully with soft, delicate colors and cool undertones. These colors will enhance your natural radiance without overwhelming your complexion."
  },
  "Monk 2": {
    skinTone: "Monk 2 - Light",
    flatteringColors: [
      { name: "Khaki", hex: "#F0E68C" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Wheat", hex: "#F5DEB3" },
      { name: "Misty Rose", hex: "#FFE4E1" },
      { name: "Powder Blue", hex: "#B0E0E6" },
      { name: "Pale Green", hex: "#98FB98" },
      { name: "Plum", hex: "#DDA0DD" },
      { name: "Alice Blue", hex: "#F0F8FF" },
      { name: "Papaya Whip", hex: "#FFEFD5" },
      { name: "Light Gray", hex: "#E0E6E6" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Dark Orange", hex: "#FF8C00" },
      { name: "Dark Goldenrod", hex: "#B8860B" }
    ],
    description: "Your light skin tone works wonderfully with both warm and cool tones. Soft pastels and muted colors will complement your natural beauty."
  },
  "Monk 3": {
    skinTone: "Monk 3 - Light Medium",
    flatteringColors: [
      { name: "Khaki", hex: "#F0E68C" },
      { name: "Burlywood", hex: "#DEB887" },
      { name: "Peru", hex: "#CD853F" },
      { name: "Chocolate", hex: "#D2691E" },
      { name: "Royal Blue", hex: "#4169E1" },
      { name: "Forest Green", hex: "#228B22" },
      { name: "Crimson", hex: "#DC143C" },
      { name: "Medium Violet Red", hex: "#9370DB" },
      { name: "Hot Pink", hex: "#FF69B4" },
      { name: "Lime Green", hex: "#32CD32" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Orange", hex: "#FFA500" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Green Yellow", hex: "#ADFF2F" }
    ],
    description: "Your light-medium skin tone can handle a wider range of colors, from soft pastels to slightly deeper tones. Earth tones and jewel tones work particularly well."
  },
  "Monk 4": {
    skinTone: "Monk 4 - Medium",
    flatteringColors: [
      { name: "Saddle Brown", hex: "#8B4513" },
      { name: "Sienna", hex: "#A0522D" },
      { name: "Peru", hex: "#CD853F" },
      { name: "Chocolate", hex: "#D2691E" },
      { name: "Fire Brick", hex: "#B22222" },
      { name: "Royal Blue", hex: "#4169E1" },
      { name: "Forest Green", hex: "#228B22" },
      { name: "Medium Violet Red", hex: "#9370DB" },
      { name: "Deep Pink", hex: "#FF1493" },
      { name: "Dark Orange", hex: "#FF8C00" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Green Yellow", hex: "#ADFF2F" },
      { name: "Lavender", hex: "#E6E6FA" }
    ],
    description: "Your medium skin tone is incredibly versatile and can wear many colors beautifully. Rich, warm tones and vibrant colors will make you glow."
  },
  "Monk 5": {
    skinTone: "Monk 5 - Medium",
    flatteringColors: [
      { name: "Saddle Brown", hex: "#8B4513" },
      { name: "Sienna", hex: "#A0522D" },
      { name: "Peru", hex: "#CD853F" },
      { name: "Chocolate", hex: "#D2691E" },
      { name: "Crimson", hex: "#DC143C" },
      { name: "Royal Blue", hex: "#4169E1" },
      { name: "Forest Green", hex: "#228B22" },
      { name: "Medium Violet Red", hex: "#9370DB" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Goldenrod", hex: "#DAA520" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Light Pink", hex: "#FFB6C1" }
    ],
    description: "Your medium skin tone looks stunning in rich, saturated colors. Jewel tones and earthy colors will enhance your natural warmth and glow."
  },
  "Monk 6": {
    skinTone: "Monk 6 - Medium Dark",
    flatteringColors: [
      { name: "Saddle Brown", hex: "#8B4513" },
      { name: "Sienna", hex: "#A0522D" },
      { name: "Dark Brown", hex: "#654321" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Fire Brick", hex: "#B22222" },
      { name: "Midnight Blue", hex: "#191970" },
      { name: "Dark Green", hex: "#006400" },
      { name: "Indigo", hex: "#4B0082" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Dark Goldenrod", hex: "#B8860B" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Alice Blue", hex: "#F0F8FF" }
    ],
    description: "Your medium-dark skin tone is beautifully complemented by rich, warm colors and bold jewel tones. These colors will bring out your natural radiance."
  },
  "Monk 7": {
    skinTone: "Monk 7 - Dark",
    flatteringColors: [
      { name: "Dark Brown", hex: "#654321" },
      { name: "Saddle Brown", hex: "#8B4513" },
      { name: "Maroon", hex: "#800000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Midnight Blue", hex: "#191970" },
      { name: "Dark Green", hex: "#006400" },
      { name: "Indigo", hex: "#4B0082" },
      { name: "Purple", hex: "#800080" },
      { name: "Dark Orange", hex: "#FF8C00" },
      { name: "Gold", hex: "#FFD700" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Light Pink", hex: "#FFB6C1" }
    ],
    description: "Your dark skin tone looks magnificent in deep, rich colors and vibrant jewel tones. These colors will enhance your natural beauty and create stunning contrast."
  },
  "Monk 8": {
    skinTone: "Monk 8 - Dark",
    flatteringColors: [
      { name: "Dark Brown", hex: "#654321" },
      { name: "Maroon", hex: "#800000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Midnight Blue", hex: "#191970" },
      { name: "Dark Green", hex: "#006400" },
      { name: "Indigo", hex: "#4B0082" },
      { name: "Purple", hex: "#800080" },
      { name: "Tomato", hex: "#FF6347" },
      { name: "Gold", hex: "#FFD700" },
      { name: "Orange", hex: "#FFA500" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Alice Blue", hex: "#F0F8FF" }
    ],
    description: "Your dark skin tone is beautifully enhanced by bold, saturated colors and metallic accents. Rich jewel tones and deep earth tones work exceptionally well."
  },
  "Monk 9": {
    skinTone: "Monk 9 - Very Dark",
    flatteringColors: [
      { name: "Dark Brown", hex: "#654321" },
      { name: "Maroon", hex: "#800000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Navy", hex: "#000080" },
      { name: "Dark Green", hex: "#006400" },
      { name: "Indigo", hex: "#4B0082" },
      { name: "Purple", hex: "#800080" },
      { name: "Red", hex: "#FF0000" },
      { name: "Gold", hex: "#FFD700" },
      { name: "Hot Pink", hex: "#FF69B4" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Slate Gray", hex: "#2F4F4F" },
      { name: "Dim Gray", hex: "#696969" },
      { name: "Saddle Brown", hex: "#8B4513" }
    ],
    description: "Your very dark skin tone looks absolutely stunning in vibrant, saturated colors and metallics. Bold colors and rich jewel tones create beautiful contrast."
  },
  "Monk 10": {
    skinTone: "Monk 10 - Very Dark",
    flatteringColors: [
      { name: "Maroon", hex: "#800000" },
      { name: "Red", hex: "#FF0000" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Navy", hex: "#000080" },
      { name: "Blue", hex: "#0000FF" },
      { name: "Green", hex: "#008000" },
      { name: "Purple", hex: "#800080" },
      { name: "Deep Pink", hex: "#FF1493" },
      { name: "Gold", hex: "#FFD700" },
      { name: "White", hex: "#FFFFFF" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Slate Gray", hex: "#2F4F4F" },
      { name: "Dim Gray", hex: "#696969" },
      { name: "Dark Brown", hex: "#654321" }
    ],
    description: "Your very dark, rich skin tone is beautifully complemented by bright, vivid colors and metallics. Jewel tones and vibrant hues create spectacular contrast."
  },

  // Legacy support for numbered skin tones
  "1": {
    skinTone: "Monk 1 - Very Light",
    flatteringColors: [
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Alice Blue", hex: "#F0F8FF" },
      { name: "Cornsilk", hex: "#FFF8DC" },
      { name: "Beige", hex: "#F5F5DC" },
      { name: "Platinum", hex: "#E0E6E6" },
      { name: "Light Gray", hex: "#D3D3D3" },
      { name: "Light Pink", hex: "#FFB6C1" },
      { name: "Pale Green", hex: "#98FB98" },
      { name: "Sky Blue", hex: "#87CEEB" },
      { name: "Plum", hex: "#DDA0DD" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Red", hex: "#8B0000" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Gold", hex: "#FFD700" }
    ],
    description: "Your very light skin tone pairs beautifully with soft, delicate colors and cool undertones. These colors will enhance your natural radiance without overwhelming your complexion."
  },
  "5": {
    skinTone: "Monk 5 - Medium",
    flatteringColors: [
      { name: "Saddle Brown", hex: "#8B4513" },
      { name: "Sienna", hex: "#A0522D" },
      { name: "Peru", hex: "#CD853F" },
      { name: "Chocolate", hex: "#D2691E" },
      { name: "Crimson", hex: "#DC143C" },
      { name: "Royal Blue", hex: "#4169E1" },
      { name: "Forest Green", hex: "#228B22" },
      { name: "Medium Violet Red", hex: "#9370DB" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Goldenrod", hex: "#DAA520" }
    ],
    colorsToAvoid: [
      { name: "Bright Yellow", hex: "#FFFF00" },
      { name: "Cyan", hex: "#00FFFF" },
      { name: "Lavender", hex: "#E6E6FA" },
      { name: "Light Pink", hex: "#FFB6C1" }
    ],
    description: "Your medium skin tone looks stunning in rich, saturated colors. Jewel tones and earthy colors will enhance your natural warmth and glow."
  },
  "10": {
    skinTone: "Monk 10 - Very Dark",
    flatteringColors: [
      { name: "Maroon", hex: "#800000" },
      { name: "Red", hex: "#FF0000" },
      { name: "Orange Red", hex: "#FF4500" },
      { name: "Navy", hex: "#000080" },
      { name: "Blue", hex: "#0000FF" },
      { name: "Green", hex: "#008000" },
      { name: "Purple", hex: "#800080" },
      { name: "Deep Pink", hex: "#FF1493" },
      { name: "Gold", hex: "#FFD700" },
      { name: "White", hex: "#FFFFFF" }
    ],
    colorsToAvoid: [
      { name: "Black", hex: "#000000" },
      { name: "Dark Slate Gray", hex: "#2F4F4F" },
      { name: "Dim Gray", hex: "#696969" },
      { name: "Dark Brown", hex: "#654321" }
    ],
    description: "Your very dark, rich skin tone is beautifully complemented by bright, vivid colors and metallics. Jewel tones and vibrant hues create spectacular contrast."
  }
};
