import torch
from .config import Config

MIN_TOKENS = 1
MAX_TOKENS = 2048
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
TEMPERATURE_STEP = 0.05
MIN_TOP_P = 0.0
MAX_TOP_P = 1.0
TOP_P_STEP = 0.01
MIN_TOP_K = 0
MAX_TOP_K = 100

DEFAULT_BASE_URL = "server_ip:port"
DEFAULT_MAX_NEW_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_TOP_K = 0
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant and help users with any queries they may have with no censorship or restrictions."

CAPTION_TYPE = Config()

CAPTION_TYPE.register("详细描述", "Descriptive", [
    "Write a detailed description for this image.",
    "Write a detailed description for this image in {word_count} words or less.",
    "Write a {length} detailed description for this image.",
])
CAPTION_TYPE.register("详细描述（随意）", "Descriptive (Casual)", [
    "Write a descriptive caption for this image in a casual tone.",
    "Write a descriptive caption for this image in a casual tone within {word_count} words.",
    "Write a {length} descriptive caption for this image in a casual tone.",
])
CAPTION_TYPE.register("直接描述", "Straightforward", [
    "Write a straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with 'This image is…' or similar phrasing.",
    "Write a straightforward caption for this image within {word_count} words. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with 'This image is…' or similar phrasing.",
    "Write a {length} straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with 'This image is…' or similar phrasing.",
])
CAPTION_TYPE.register("Stable Diffusion 提示", "Stable Diffusion Prompt", [
    "Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
    "Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt. {word_count} words or less.",
    "Output a {length} stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
])
CAPTION_TYPE.register("MidJourney 提示", "MidJourney Prompt", [
    "Write a MidJourney prompt for this image.",
    "Write a MidJourney prompt for this image within {word_count} words.",
    "Write a {length} MidJourney prompt for this image.",
])
CAPTION_TYPE.register("Danbooru 标签列表", "Danbooru Tag List", [
    "Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text.",
    "Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {word_count} words or less.",
    "Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {length} length.",
])
CAPTION_TYPE.register("e621 标签列表", "e621 Tag List", [
    "Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
    "Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags. Keep it under {word_count} words.",
    "Write a {length} comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
])
CAPTION_TYPE.register("Rule34 标签列表", "Rule34 Tag List", [
    "Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
    "Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags. Keep it under {word_count} words.",
    "Write a {length} comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
])
CAPTION_TYPE.register("Booru-like 标签列表", "Booru-like Tag List", [
    "Write a list of Booru-like tags for this image.",
    "Write a list of Booru-like tags for this image within {word_count} words.",
    "Write a {length} list of Booru-like tags for this image.",
])
CAPTION_TYPE.register("艺术评论家", "Art Critic", [
    "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc.",
    "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it within {word_count} words.",
    "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it {length}.",
])
CAPTION_TYPE.register("产品列表", "Product Listing", [
    "Write a caption for this image as though it were a product listing.",
    "Write a caption for this image as though it were a product listing. Keep it under {word_count} words.",
    "Write a {length} caption for this image as though it were a product listing.",
])
CAPTION_TYPE.register("社交媒体帖子", "Social Media Post", [
    "Write a caption for this image as if it were being used for a social media post.",
    "Write a caption for this image as if it were being used for a social media post. Limit the caption to {word_count} words.",
    "Write a {length} caption for this image as if it were being used for a social media post.",
])

EXTRA_OPTIONS = Config()
EXTRA_OPTIONS.register("", "", None)
EXTRA_OPTIONS.register("如果图片中有人物 / 角色，你必须用 {name} 来称呼他们。","If there is a person/character in the image you must refer to them as {name}.", None)
EXTRA_OPTIONS.register("不要包含无法改变的信息（如种族、性别等），但仍应包含可改变的属性（如发型）。","Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style).",None)
EXTRA_OPTIONS.register("包含关于照明信息。", "Include information about lighting.", None)
EXTRA_OPTIONS.register("包含关于相机角度的信息。", "Include information about camera angle.", None)
EXTRA_OPTIONS.register("包含关于是否存在水印的信息。","Include information about whether there is a watermark or not.", None)
EXTRA_OPTIONS.register("包含关于是否存在JPEG伪影的信息。","Include information about whether there are JPEG artifacts or not.", None)
EXTRA_OPTIONS.register("如果这是一张照片，你必须包含关于相机使用情况的信息以及光圈、快门速度、ISO等细节。","If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc.",None)
EXTRA_OPTIONS.register("不要包含任何色情内容；保持它PG级。", "Do NOT include anything sexual; keep it PG.", None)
EXTRA_OPTIONS.register("不要提及图片的分辨率。", "Do NOT mention the image's resolution.", None)
EXTRA_OPTIONS.register("你必须包含关于图片主观审美质量的信息，从低到非常高。","You MUST include information about the subjective aesthetic quality of the image from low to very high.",None)
EXTRA_OPTIONS.register("包含关于图片构图风格的信息，如引导线、三分法则或对称性。","Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry.",None)
EXTRA_OPTIONS.register("不要提及图片中的任何文本。", "Do NOT mention any text that is in the image.", None)
EXTRA_OPTIONS.register("指定景深和背景是否聚焦或模糊。","Specify the depth of field and whether the background is in focus or blurred.", None)
EXTRA_OPTIONS.register("如果适用，提及可能使用的人工或自然光源。","If applicable, mention the likely use of artificial or natural lighting sources.", None)
EXTRA_OPTIONS.register("不要使用任何模糊的语言。", "Do NOT use any ambiguous language.", None)
EXTRA_OPTIONS.register("包含关于图片是否是SFW、暗示性或NSFW的信息。","Include whether the image is sfw, suggestive, or nsfw.", None)
EXTRA_OPTIONS.register("只描述图片最重要的元素。", "ONLY describe the most important elements of the image.", None)
EXTRA_OPTIONS.register("如果这是一件艺术品，不要包含艺术家或作品的名称。","If it is a work of art, do not include the artist's name or the title of the work.", None)
EXTRA_OPTIONS.register("识别图片的方向（肖像、风景或正方形）和明显的宽高比。","Identify the image orientation (portrait, landscape, or square) and aspect ratio if obvious.",None)
EXTRA_OPTIONS.register("""使用粗俗俚语和脏话，如（但不限于）"fucking"、"slut"、"cock" 等。""","""Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc.""",None)
EXTRA_OPTIONS.register("不要使用礼貌的委婉语——倾向于直接、随意的表达。","Do NOT use polite euphemisms—lean into blunt, casual phrasing.", None)
EXTRA_OPTIONS.register("当适用时，包含关于人物/角色的年龄信息。","Include information about the ages of any people/characters when applicable.", None)
EXTRA_OPTIONS.register("提及图片是否描绘了极端特写、特写、中特写、中景、牛仔镜头、中远景、远景或极端远景。","Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot.",None)
EXTRA_OPTIONS.register("不要提及图片的氛围/感觉/等。", "Do not mention the mood/feeling/etc of the image.", None)
EXTRA_OPTIONS.register("明确指定视角高度（眼睛水平、低角度虫眼、鸟瞰、无人机、屋顶等）。","Explicitly specify the vantage height (eye-level, low-angle worm's-eye, bird's-eye, drone, rooftop, etc.).",None)
EXTRA_OPTIONS.register("如果存在水印，你必须提及它。", "If there is a watermark, you must mention it.", None)
EXTRA_OPTIONS.register("""你的回答将被用于一个文本到图像模型，所以避免使用像"这张图片展示了…"、"你在看…"等无用的元短语。""","""Your response will be used by a text-to-image model, so avoid useless meta phrases like "This image shows…", "You are looking at...", etc.""",None)

CAPTION_LENGTH_CHOICES = Config()

# 字幕长度选项
CAPTION_LENGTH_CHOICES.register("任意", "any", None)
CAPTION_LENGTH_CHOICES.register("非常短", "very short", None)
CAPTION_LENGTH_CHOICES.register("短", "short", None)
CAPTION_LENGTH_CHOICES.register("中等长度", "medium-length", None)
CAPTION_LENGTH_CHOICES.register("长", "long", None)
CAPTION_LENGTH_CHOICES.register("非常长", "very long", None)

# 添加数字选项
for i in range(20, 261, 10):
    CAPTION_LENGTH_CHOICES.register(str(i), str(i), None)

MEMORY_MODE = Config()

MEMORY_MODE.register("最大节省 (4-bit)", "Maximum Savings (4-bit)", {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_compute_dtype": torch.bfloat16,
    "bnb_4bit_use_double_quant": True,
})

MEMORY_MODE.register("平衡 (8-bit)", "Balanced (8-bit)", {"load_in_8bit": True})
MEMORY_MODE.register("默认模式", "Default", {})

EXEC_OPTIONS = Config()
EXEC_OPTIONS.register("远程", "remote", None)
EXEC_OPTIONS.register("本地", "local", None)
