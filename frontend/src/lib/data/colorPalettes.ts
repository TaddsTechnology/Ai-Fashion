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
  }
}; 