import shutil
import zipfile

from loguru import logger
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, opentype, Glyph
from pixel_font_builder.opentype import Flavor

from tools import path_define, options
from tools.utils.psffont import PsfFont


def main():
    if path_define.build_dir.exists():
        shutil.rmtree(path_define.build_dir)
    path_define.outputs_dir.mkdir(parents=True)
    path_define.releases_dir.mkdir(parents=True)

    psf_font = PsfFont.load(path_define.src_dir.joinpath('TokiFicMinchoCL-Regular.pfs'))

    builder = FontBuilder()
    builder.font_metric.font_size = psf_font.em_size
    builder.font_metric.horizontal_layout.ascent = psf_font.ascend
    builder.font_metric.horizontal_layout.descent = psf_font.descend
    builder.opentype_config.has_vertical_metrics = False  # 无垂直布局

    builder.meta_info.version = '0.0.0'
    builder.meta_info.family_name = psf_font.name
    builder.meta_info.weight_name = WeightName(psf_font.style)
    builder.meta_info.serif_style = SerifStyle.SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_style = WidthStyle.PROPORTIONAL
    builder.meta_info.designer = psf_font.author
    builder.meta_info.vendor_url = 'https://github.com/Fuur-Cho/TokiFic'

    # 必须存在一个 .notdef 字形
    builder.glyphs.append(Glyph(
        name='.notdef',
        advance_width=psf_font.width,
    ))

    for code_point, psf_glyph in sorted(psf_font.glyphs.items()):
        # 预览字形
        print(f'char: {chr(code_point)} ({code_point:04X})')
        for bitmap_row in psf_glyph.bitmap:
            text = ''.join('  ' if color == 0 else '██' for color in bitmap_row)
            print(f'{text}*')
        print()

        glyph_name = f'u{code_point:04X}'
        builder.glyphs.append(Glyph(
            name=glyph_name,
            horizontal_offset=(psf_glyph.left_offset, psf_glyph.baseline - psf_glyph.height),
            advance_width=psf_glyph.width,
            bitmap=psf_glyph.bitmap,
        ))
        if __name__ == '__main__':
            builder.character_mapping[code_point] = glyph_name

    font_file_paths = []
    for font_format in options.font_formats:
        file_path = path_define.outputs_dir.joinpath(f'TokiFicMinchoCL-{psf_font.style}.{font_format}')
        if font_format == 'otf.woff':
            builder.save_otf(file_path, flavor=Flavor.WOFF)
        elif font_format == 'otf.woff2':
            builder.save_otf(file_path, flavor=Flavor.WOFF2)
        elif font_format == 'ttf.woff':
            builder.save_ttf(file_path, flavor=Flavor.WOFF)
        elif font_format == 'ttf.woff2':
            builder.save_ttf(file_path, flavor=Flavor.WOFF2)
        else:
            getattr(builder, f'save_{font_format}')(file_path)
        font_file_paths.append(file_path)
        logger.info("Make font: '{}'", file_path)

    with zipfile.ZipFile(path_define.releases_dir.joinpath(f'TokiFicMinchoCL.zip'), 'w') as file:
        for file_path in font_file_paths:
            file.write(file_path, file_path.name)
        logger.info(f'Create release zip')


if __name__ == '__main__':
    main()
