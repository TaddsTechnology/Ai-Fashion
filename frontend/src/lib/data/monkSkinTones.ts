export interface MonkSkinTone {
  id: string;
  name: string;
  hexCode: string;
  description: string;
  userFriendlyName: string; // New field for seasonal color analysis names
  seasonalType: string; // Seasonal color type for better understanding
  flatteringColors: {
    name: string;
    hex: string;
  }[];
  colorsToAvoid: {
    name: string;
    hex: string;
  }[];
}

export const monkSkinTones: Record<string, MonkSkinTone> = {
  "Monk01": {
    id: "Monk01",
    name: "Monk 01",
    userFriendlyName: "Light Summer",
    seasonalType: "Cool & Light",
    hexCode: "#f6ede4",
    description: "Very fair skin with cool or neutral undertones. Colors with blue or purple undertones will complement this skin tone beautifully.",
    flatteringColors: [
      { name: "Navy", hex: "#003057" },
      { name: "Soft Pink", hex: "#F395C7" },
      { name: "Lavender", hex: "#A277A6" },
      { name: "Emerald", hex: "#009775" },
      { name: "Burgundy", hex: "#890C58" },
      { name: "Cobalt Blue", hex: "#0057B8" },
    ],
    colorsToAvoid: [
      { name: "Orange", hex: "#FF8200" },
      { name: "Warm Yellow", hex: "#FFCD00" },
      { name: "Camel", hex: "#CDA788" },
      { name: "Olive", hex: "#A09958" },
    ]
  },
  "Monk02": {
    id: "Monk02",
    name: "Monk 02",
    userFriendlyName: "Light Spring",
    seasonalType: "Light & Fresh",
    hexCode: "#f3e7db",
    description: "Fair skin with neutral to cool undertones. Soft, cool colors will enhance your natural complexion.",
    flatteringColors: [
      { name: "Powder Blue", hex: "#9BCBEB" },
      { name: "Soft Plum", hex: "#86647A" },
      { name: "Dusty Rose", hex: "#D592AA" },
      { name: "Slate Blue", hex: "#57728B" },
      { name: "Soft Teal", hex: "#00B0B9" },
      { name: "Mauve", hex: "#C4A4A7" },
    ],
    colorsToAvoid: [
      { name: "Bright Orange", hex: "#FF8200" },
      { name: "Neon Yellow", hex: "#FCE300" },
      { name: "Terracotta", hex: "#A6631B" },
      { name: "Mustard", hex: "#B89D18" },
    ]
  },
  "Monk03": {
    id: "Monk03",
    name: "Monk 03",
    userFriendlyName: "Warm Spring",
    seasonalType: "Warm & Bright",
    hexCode: "#f7ead0",
    description: "Light skin with warm, peachy undertones. Warm, soft colors will enhance your natural glow.",
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
    ]
  },
  "Monk04": {
    id: "Monk04",
    name: "Monk 04",
    userFriendlyName: "Clear Spring",
    seasonalType: "Clear & Vibrant",
    hexCode: "#eadaba",
    description: "Light to medium skin with warm, golden undertones. Warm, clear colors will complement your complexion.",
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
    ]
  },
  "Monk05": {
    id: "Monk05",
    name: "Monk 05",
    userFriendlyName: "Soft Autumn",
    seasonalType: "Warm & Muted",
    hexCode: "#d7bd96",
    description: "Medium skin with neutral to warm undertones. Rich, warm colors will enhance your natural warmth.",
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
    ]
  },
  "Monk06": {
    id: "Monk06",
    name: "Monk 06",
    userFriendlyName: "Warm Autumn",
    seasonalType: "Rich & Earthy",
    hexCode: "#a07e56",
    description: "Medium to deep skin with warm, golden undertones. Rich, earthy colors will complement your complexion.",
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
    ]
  },
  "Monk07": {
    id: "Monk07",
    name: "Monk 07",
    userFriendlyName: "Deep Autumn",
    seasonalType: "Deep & Warm",
    hexCode: "#825c43",
    description: "Deep skin with warm, rich undertones. Bold, vibrant colors will enhance your natural richness.",
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
    ]
  },
  "Monk08": {
    id: "Monk08",
    name: "Monk 08",
    userFriendlyName: "Deep Winter",
    seasonalType: "Bold & Dramatic",
    hexCode: "#604134",
    description: "Deep skin with neutral to warm undertones. Rich, vibrant colors will complement your complexion beautifully.",
    flatteringColors: [
      { name: "Hot Pink", hex: "#E3006D" },
      { name: "Cobalt Blue", hex: "#0057B8" },
      { name: "True Red", hex: "#CE0037" },
      { name: "Violet", hex: "#963CBD" },
      { name: "Emerald", hex: "#009775" },
      { name: "Gold", hex: "#FFB81C" },
    ],
    colorsToAvoid: [
      { name: "Muted Olive", hex: "#A3AA83" },
      { name: "Dusty Rose", hex: "#C4A4A7" },
      { name: "Light Pastels", hex: "#F1EB9C" },
      { name: "Beige", hex: "#D3BC8D" },
    ]
  },
  "Monk09": {
    id: "Monk09",
    name: "Monk 09",
    userFriendlyName: "Cool Winter",
    seasonalType: "Cool & Intense",
    hexCode: "#3a312a",
    description: "Deep skin with cool undertones. Bold, jewel-toned colors will enhance your natural depth.",
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
    ]
  },
  "Monk10": {
    id: "Monk10",
    name: "Monk 10",
    userFriendlyName: "Clear Winter",
    seasonalType: "Vibrant & Contrasting",
    hexCode: "#292420",
    description: "Very deep skin with neutral to cool undertones. Bold, bright colors will create a stunning contrast with your complexion.",
    flatteringColors: [
      { name: "Hot Pink", hex: "#E3006D" },
      { name: "Cobalt Blue", hex: "#0057B8" },
      { name: "True Red", hex: "#CE0037" },
      { name: "Bright Yellow", hex: "#FFCD00" },
      { name: "Emerald", hex: "#009775" },
      { name: "White", hex: "#FEFEFE" },
    ],
    colorsToAvoid: [
      { name: "Muted Olive", hex: "#A3AA83" },
      { name: "Dusty Rose", hex: "#C4A4A7" },
      { name: "Terracotta", hex: "#A6631B" },
      { name: "Brown", hex: "#5C462B" },
    ]
  }
}; 