# Tools:Q View Layer Loader

[English](README.en.md)

## 概要

View 3D / ALL Mode

全てのView Layer内にある各レイヤーの設定を指定したBlendファイルから読み込む。

## UI

- Blend Path
  - 読み込み対象のBlendファイルを指定する。
- モード
  - 曖昧一致
    - 各プロジェクト毎の命名規則に従って、共通しているレイヤーを同一と見做して復元する。 
    - (例: charaA_mdlとcharaB_mdl、charaA_hairとcharaB_hair等)
  - 完全一致
    - 保存したときの名前と完全に一致しているもののみ復元する。
  - 同一合成
    - 同一アセットを読み込んだ際に「.001」などサフィックスが付いているものをサフィックス無しのViewLayerとして合成する。
- Load
  - 読み込む

## 動画

[![YouTubeで見る](https://img.youtube.com/vi/gqhgJspHUXs/0.jpg)](https://www.youtube.com/watch?v=gqhgJspHUXs)

## インストール

Project Studio Qが公開している [Tools:Q](https://github.com/Project-StudioQ/toolsq_common) よりインストールしてください。

## ライセンス

このBlenderアドオンは GNU Public License v2 です。
