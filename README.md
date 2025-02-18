# 2025-seccon13-workshop
SECCON13(2025年) (https://www.seccon.jp/13/ep250301.html) ・「バッジ基板でマイコンハンダ付け＆プログラミングワークショップ」準備用レポジトリ

参考: https://learn.adafruit.com/welcome-to-circuitpython

## プログラム
- btn_oled: SECCON13のボード上の赤、緑、青、白ボタンを押すとOLEDディスプレイ上に対応した色の名前が表示されるプログラム
- pingpong: Ping-Pongゲームのプログラム
- pingpong_optimized: pingpongの改良版で、ディスプレイの更新を少なくして高速化している

## 手順
### 1. ボードにCircuitPythonをインストール
参考: https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython

### 2. ライブラリバンドルをダウンロード 
参考: https://learn.adafruit.com/welcome-to-circuitpython/circuitpython-libraries

### 3. 以下のライブラリをボードの`/lib`フォルダに入れる 
- `adafruit_ticks.mpy` 
- `adafruit_framebuf.mpy` 
- `adafruit_ssd1306.mpy` 
- `asyncio` (フォルダごと)

### 4. 以下のフォントをボードの`/`に`font5x8.bin`として入れる
https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/font5x8.bin

### 5. ボードの`/code.py`にプログラムを書き込む

## デバッグ方法
### 方法1. Mu Editorをインストールする
https://codewith.mu

### 方法2. `screen`コマンドでシリアル接続する
#### 1. デバイスを接続せずに以下を打つ
```bash
ls /dev/tty.*
```
#### 2. デバイスを接続してもう一度以下を打ち、デバイスを特定
```bash
ls /dev/tty.*
```
#### 3. 接続
```bash
screen /dev/tty.board_name 115200
```
(もし`$TERM too long - sorry.`と言われたら、`export TERM=xterm-256color`を打ったあとにscreenコマンドを実行してください)