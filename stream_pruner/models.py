class Track:
    def __init__(self, track_json: dict):
        self.raw: dict = track_json
        self.id: int = track_json["id"]
        self.type: str = track_json["type"]
        self.properties: dict = track_json["properties"]
        self.default: bool = self.properties.get("default_track", False)
        self.enabled: bool = self.properties.get("enabled_track", False)
        self.original: bool = self.properties.get("flag_original", False)
        self.forced_prop: bool = self.properties.get("forced_track", False)
        self.language: str = self.properties.get("language", "und")
        self.track_name: str = self.properties.get("track_name", "")
        self.codec = self.properties.get("codec_id", "")[2:]

    @property
    def forced(self) -> bool:
        return self.forced_prop or "forced" in self.track_name.lower()


class VideoTrack(Track):
    pass


class AudioTrack(Track):
    def __str__(self):
        track_name = self.track_name or "<und>"
        return f"[{self.id}][{self.codec}].{self.language}: {track_name} (Enabled: {self.enabled}, Original: {self.original}), Default: {self.default}, Forced: {self.forced}"

    def __repr__(self):
        return str(self)


class SubtitleTrack(Track):
    def __init__(self, track_json: dict):
        super().__init__(track_json)
        self.hearing_impaired_prop: bool = self.properties.get(
            "flag_hearing_impaired", False
        )

    @property
    def hearing_impaired(self) -> bool:
        return self.hearing_impaired_prop or "SDH" in self.track_name.lower()

    @property
    def vobsub(self) -> bool:
        return self.codec == "VOBSUB"

    def __str__(self):
        track_name = self.track_name or "<und>"
        return f"[{self.id}].{self.language}: {track_name} (Enabled: {self.enabled}, Original: {self.original}, Default: {self.default}, Forced: {self.forced})"

    def __repr__(self):
        return str(self)


class MkvData:
    def __init__(self, path: str, raw_data: dict):
        self.path: str = path
        self.raw: dict = raw_data
        self.video_tracks: list[VideoTrack] = []
        self.audio_tracks: list[AudioTrack] = []
        self.subtitle_tracks_list: list[SubtitleTrack] = []
        self.subtitle_tracks: dict[str, list[SubtitleTrack]] = {}
        self.other_tracks: list[Track] = []
        for track in sorted(self.raw["tracks"], key=lambda t: t["id"]):
            if track["type"] == "video":
                self.video_tracks.append(VideoTrack(track))
            elif track["type"] == "audio":
                self.audio_tracks.append(AudioTrack(track))
            elif track["type"] == "subtitles":
                sub_track = SubtitleTrack(track)
                self.subtitle_tracks_list.append(sub_track)
                self.subtitle_tracks.setdefault(sub_track.language, []).append(
                    sub_track
                )
            else:
                self.other_tracks.append(Track(track))

    def is_valid(self) -> bool:
        return bool(self.video_tracks and self.audio_tracks and self.subtitle_tracks)
