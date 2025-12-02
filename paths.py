from pathlib import Path

# Racine du proje
ROOT = Path(__file__).resolve().parent


# Sous-dossiers
ARCHIVES_VIDEOS = ROOT / "archives_videos"
PIPELINE_CSV = ROOT / "pipeline_csv"
VIDEO_GENERATOR = ROOT / "video_generator"
VIDEO_PUBLISH = ROOT / "video_publish"


# \VIDEO_GENERATOR
VG_DEPLOYMENTFOLDER = VIDEO_GENERATOR / "deployment_folder"
VG_TEMP = VIDEO_GENERATOR / "temp"
VG_TEST_VOICES = VIDEO_GENERATOR / "test_voices"
VG_VIDEOS_EDITED = VIDEO_GENERATOR / "videos_edited"

# \VIDEO_GENERATOR\TEMP\
VG_T_VOICEOVER = VG_TEMP / "voiceovers"
VG_T_VIDEOS = VG_TEMP / "temporary_videos"


# \VIDEO_PUBLISH
VP_INSTAGRAM = VIDEO_PUBLISH / "instagram"
VP_YOUTUBE = VIDEO_PUBLISH / "youtube"


# \VIDEO_PUBLISH\YOUTUBE\
VP_YT_OAUTH = VP_YOUTUBE / "oauth"