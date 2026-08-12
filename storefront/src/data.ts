export type Option = { id: string; label: string; values: string[]; required?: boolean }

export type Product = {
  id: string
  name: string
  brand: string
  model: string
  price: number
  compareAt?: number
  category: string
  roles: string[]
  image: string
  description: string
  fit: string
  options: Option[]
  sourceUrl: string
  sourceImage: string
}

export const NOTICE = 'New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.'
export const EMAIL = 'orders@mtuniforms.com'
export const PHONE = '(814) 536-2390'

const asset = (name: string) => `/assets/${name}`

export const PRODUCTS: Product[] = [
  {
    id: 'parka',
    name: 'Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka',
    brand: 'Portwest', model: 'HV5-1P', price: 159.98, compareAt: 299.99,
    category: 'Outerwear', roles: ['Fire & EMS', 'Security', 'Police'],
    image: asset('d269c3c8148366cd9a50cb138bb58fec229080eeccde08ebe0a68ded94a56baa.jpg'),
    description: 'Waterproof, windproof, breathable outer shell with sealed seams, drop-in hood, pit zips, and rain-shed yokes.',
    fit: 'Public snapshot lists Alpha Size with X-Large shown. Confirm your size with the team before requesting.',
    options: [{ id: 'size', label: 'Size', values: ['X-Large'], required: true }],
    sourceUrl: 'https://mtuniforms.com/SPIEWAK-VIZGUARD-RESCUE-PARKA-WATERPROOF-BLOOD-BORNE-PATHOGEN-RESISTANT',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Outerwear/s588vtr_006_0-550x550h.jpg',
  },
  {
    id: 'trousers',
    name: 'Elbeco Tek2 Cargo Pocket Trousers',
    brand: 'Elbeco', model: 'TRTTCPO', price: 58.98, compareAt: 79.99,
    category: 'Pants', roles: ['Police', 'Fire & EMS', 'Corrections'],
    image: asset('74d50994de2984e114e378f4dd8c92f57fff021e3739fac6abc0307609527640.jpg'),
    description: 'Stretch twill cargo trousers with a Covert Flex waistband, fluid resistance, reflective tape, and relaxed action fit.',
    fit: 'Closeout public snapshot: no exchange or return. Use the waist and inseam fields to make your request specific.',
    options: [
      { id: 'waist', label: 'Waist', values: ['30', '32', '34', '36', '38', '40', '42'], required: true },
      { id: 'inseam', label: 'Inseam', values: ['28', '30', '32', '34', '35'], required: true },
      { id: 'color', label: 'Color', values: ['Dark Navy'], required: true },
    ],
    sourceUrl: 'https://mtuniforms.com/elbeco-tek2-cargo-pocket-trousers-trttcpo',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Pants/covert%20waistband-550x550h.jpg',
  },
  {
    id: 'postal-shirt',
    name: 'USPS Letter Carrier Performance Knit Shirt',
    brand: 'Elbeco', model: 'PSTPK', price: 42.99,
    category: 'Shirts', roles: ['Postal'],
    image: asset('1d8171ec58d145a783246357566377929b0020bdc09fbaef5ec8f9c5e0807663.jpg'),
    description: 'Performance knit with soil-release finish, moisture wicking, banded collar, three-button placket, and elongated tail.',
    fit: 'Public snapshot offers Small through XXX-Large and a Regular length. Confirm uniform specifications with the team.',
    options: [
      { id: 'size', label: 'Size', values: ['Small', 'Medium', 'Large', 'X-Large', 'XX-Large', 'XXX-Large'], required: true },
      { id: 'sleeve', label: 'Sleeve', values: ['Regular'], required: true },
    ],
    sourceUrl: 'https://mtuniforms.com/new-usps-letter-carrier-performance-knit-shirt-pstpk',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Postal/LC%20KNIT-550x550h.jpg',
  },
  {
    id: 'cap',
    name: 'W. Alboum Cushion Air Pershing Style Uniform Cap',
    brand: 'W. Alboum Hat Company', model: 'HTP', price: 58.99,
    category: 'Headwear', roles: ['Police', 'Fire & EMS', 'PA Constable', 'Security'],
    image: asset('9f7bf62d0dab56c43af0c4dfc17ca7600932284eba7fac15df849c47d16da635.jpg'),
    description: 'Cushion Air cap with cloth band, black vinyl strap, and choice of department button and hardware finish.',
    fit: 'Sizes span Small (6 5/8–6 3/4) through 2XL (7 3/4–8). A team member can confirm the correct fit.',
    options: [
      { id: 'size', label: 'Size', values: ['Small', 'Medium', 'Large', 'X-Large', 'XX-Large'], required: true },
      { id: 'button', label: 'Button', values: ['P Button', 'FD Button'], required: true },
      { id: 'finish', label: 'Finish', values: ['Silver', 'Gold'], required: true },
    ],
    sourceUrl: 'https://mtuniforms.com/w-alboum-cushion-air-pershing-style-uniform-cap-htrt',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Headwear/round-top-550x550w.jpg',
  },
  {
    id: 'vest',
    name: 'Adjustable High Visibility Break Away Safety Vest',
    brand: 'M.T. Uniforms public snapshot', model: 'VSTAPS', price: 16.99,
    category: 'Hi-Visibility', roles: ['Police', 'Fire & EMS', 'Security', 'Corrections'],
    image: asset('606ddfa707c44874da1ed1c8edf2d58653bded851ec79b0f4bb7f8482ea45afd.jpg'),
    description: 'Mesh polyester safety vest with five-point tear-away construction, reflective stripes, adjustable side straps, and pockets.',
    fit: 'Choose Regular (S–XL) or Plus (2XL–5XL). The public snapshot shows a $5.00 Plus option note.',
    options: [{ id: 'size', label: 'Size', values: ['Regular (S–XL)', 'Plus (2XL–5XL)'], required: true }],
    sourceUrl: 'https://mtuniforms.com/adjustable-high-visibility-break-away-safety-vest-vstaps',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Outerwear/LVM2-PSV-F1100_1024x1024-550x550.jpg',
  },
  {
    id: 'bag',
    name: '5.11 Tactical Wingman Nylon Equipment Bag',
    brand: '5.11 Tactical', model: 'GBD', price: 110.99,
    category: 'Equipment', roles: ['Police', 'Fire & EMS', 'Security', 'Corrections'],
    image: asset('f3bb10376c9a347e90d7a60e4357b9e66b98b91479c04706be28a47dfe15104f.jpg'),
    description: '600D polyester patrol bag with adjustable divider, mesh pockets, YKK zippers, ID window, and 39-liter capacity.',
    fit: 'Designed for a passenger seat; public snapshot lists a 13.25” H × 18.5” L × 7.5” D main compartment.',
    options: [{ id: 'color', label: 'Color', values: ['Black'], required: true }],
    sourceUrl: 'https://mtuniforms.com/5-11-tactical-wingman-nylon-equipment-bag-gbd',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Bags,form%20holders/511-wingman-bag-550x550w.jpg',
  },
  {
    id: 'chevrons',
    name: 'Embroidered Sergeant Chevrons',
    brand: "Hero's Pride", model: 'EMSGT', price: 5.99,
    category: 'Insignia', roles: ['Police', 'Corrections', 'Postal'],
    image: asset('23b8c837cdb88630c233f10e48d9cbf9877a13a7d06a78946add0f1a2905fefb.jpg'),
    description: 'Pair Sergeant chevrons, 3 inches wide, with public snapshot colorways for a focused request.',
    fit: 'Specify the thread colorway so the team can confirm the correct insignia.',
    options: [{ id: 'color', label: 'Color', values: ['Medium Gold, Black', 'Royal Blue, Black, White', 'Silver, Black', 'Medium Gold, Dark Navy'], required: true }],
    sourceUrl: 'https://mtuniforms.com/embroidered-sergeant-chevrons-emcpl',
    sourceImage: 'https://mtuniforms.com/image/cache/catalog/Emblems/rblublk-550x550h.jpg',
  },
]

export const ROLES = ['Police', 'Fire & EMS', 'PA Constable', 'Corrections', 'Security', 'Postal']
export const CATEGORIES = ['All', 'Outerwear', 'Pants', 'Shirts', 'Headwear', 'Hi-Visibility', 'Equipment', 'Insignia']
