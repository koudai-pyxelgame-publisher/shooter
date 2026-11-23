import pyxel
import math
import random

W,H = 160,120#画面の幅、高さ



class Game:
    def __init__(self):
        """コンストラクタ"""
        #puxel起動
        pyxel.init(W,H,title="hello,Pyxel!!")#右からwidth(幅),height(高さ),title(タイトルバーの名前),fps(フレームレート),quit_key(閉じるキー指定),display_scale(表示倍率),capture_scale(録画の画質),capture_sec(録画最大秒数)
        pyxel.run(self.update,self.draw)
    def update(self):
        """更新処理"""
        
    def draw(self):
        """描画処理"""
        pyxel.cls(0)
        pass
    
    def draw_text(self,x=W/2,y=H/2,text="text",col=14):#真ん中でテキスト描画
        pyxel.text (x-2*len(text) , y-3, text , col )

def main():
    """メイン処理"""
    Game()

if __name__ == "__main__":
    main()
        