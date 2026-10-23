"""Regression coverage for read-only AIOS workbench discovery and bounded scanning."""
from pathlib import Path
from um.scan import Index, aios_games

def test_aios_root_is_shallow_and_not_an_install(tmp_path):
    games=tmp_path/"GAMES"
    (games/"TDR2000"/"02_STATIC").mkdir(parents=True)
    (games/"WRECKFEST").mkdir()
    (games/".hidden").mkdir()
    (games/"TDR2000"/"02_STATIC"/"old.exe").write_bytes(b"MZ")
    entries=aios_games(tmp_path)
    assert [e["name"] for e in entries]==["TDR2000","WRECKFEST"]
    assert all(e["status"]=="workbench-directory-not-install" for e in entries)

def test_index_preserves_real_case_and_avoids_rewalking(tmp_path, monkeypatch):
    (tmp_path/"ASSETS").mkdir()
    expected=tmp_path/"ASSETS"/"Game.EXE"
    expected.write_bytes(b"MZ")
    ix=Index(tmp_path)
    assert ix.path("assets/game.exe")==expected
    # If resolution re-enumerates directory contents this now raises.
    monkeypatch.setattr(Path, "iterdir", lambda _: (_ for _ in ()).throw(AssertionError("walked twice")))
    assert ix.path("assets/game.exe")==expected
