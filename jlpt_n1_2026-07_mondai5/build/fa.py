# Forced alignment + teacher-forced scoring with Whisper small (CTranslate2) via faster-whisper internals.
import wave, numpy as np, math, sys, json
from faster_whisper import WhisperModel
from faster_whisper.tokenizer import Tokenizer
from faster_whisper.audio import pad_or_trim

SR = 16000
class FA:
    def __init__(self, model_dir, wav, offset):
        self.m = WhisperModel(model_dir, device="cpu", compute_type="int8", cpu_threads=4)
        self.tok = Tokenizer(self.m.hf_tokenizer, True, task="transcribe", language="ja")
        wf = wave.open(wav, "rb")
        self.audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        self.offset = offset

    def _enc(self, t0, t1):
        a = self.audio[int((t0 - self.offset) * SR): int((t1 - self.offset) * SR)]
        feats = self.m.feature_extractor(a)
        num_frames = feats.shape[-1]
        assert num_frames <= 3000, (t0, t1, num_frames)
        seg = pad_or_trim(feats)
        enc = self.m.encode(seg)
        return enc, num_frames

    def align(self, t0, t1, text):
        enc, nf = self._enc(t0, t1)
        toks = self.tok.encode(text)
        res = self.m.find_alignment(self.tok, [toks], enc, nf)[0]
        # total log prob from token probs
        r = self.m.model.align(enc, self.tok.sot_sequence, [toks], nf)[0]
        lp = float(np.sum(np.log(np.maximum(np.array(r.text_token_probs), 1e-9))))
        words = [dict(w=x["word"], s=round(x["start"] + t0, 3), e=round(x["end"] + t0, 3), p=round(float(x["probability"]), 3)) for x in res]
        return words, lp, len(toks)

    def score(self, t0, t1, texts):
        enc, nf = self._enc(t0, t1)
        out = []
        for t in texts:
            toks = self.tok.encode(t)
            r = self.m.model.align(enc, self.tok.sot_sequence, [toks], nf)[0]
            probs = np.maximum(np.array(r.text_token_probs), 1e-9)
            out.append((float(np.sum(np.log(probs))), len(toks), t))
        return out

    def transcribe_window(self, t0, t1, prompt=None, beam=5):
        a = self.audio[int((t0 - self.offset) * SR): int((t1 - self.offset) * SR)]
        segs, _ = self.m.transcribe(a, language="ja", beam_size=beam, word_timestamps=False,
                                    condition_on_previous_text=False, vad_filter=False, temperature=0.0,
                                    initial_prompt=prompt)
        return [(round(s.start + t0, 2), round(s.end + t0, 2), s.text) for s in segs]
