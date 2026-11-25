import pyxel
import math
import random


#----------ゲームの定数----------
W,H = 160,120#画面の幅、高さ
game_frame_count=0
player_speed=1
invincible_frame=25#無敵フレーム
fire_rate_frame=6#発射硬直フレーム
fire_rate_up_time=200#発射速度アップ有効フレーム
dash_freeze_frame=30#ダッシュ硬直フレーム
dash_frame=5#ダッシュ継続フレーム
bullet_speed=2
enemy_max=10
#敵の確率
enemy_stage_level_list={
    "stage_0":{
        "enemy_max":0,
        "level_1":0,
        "level_2":0,
        "level_3":0
    },"stage_1":{
        "enemy_max":10,
        "level_1":100,
        "level_2":0,
        "level_3":0
    },"stage_2":{
        "enemy_max":13,
        "level_1":50,
        "level_2":50,
        "level_3":0
    },"stage_3":{
        "enemy_max":13,
        "level_1":0,
        "level_2":100,
        "level_3":0
    },"stage_4":{
        "enemy_max":12,
        "level_1":0,
        "level_2":50,
        "level_3":50
    },"stage_5":{
        "enemy_max":15,
        "level_1":20,
        "level_2":50,
        "level_3":30
        }
        }
#＃アイテムの出現確率リスト
item_probability_list={
    "None":91,#何も出ない
    "healing":5,#回復
    "fire_rate_up":4#連射速度アップ
}
character_se_ch=1#ゲームの効果音のチャンネル番号
system_sound_ch=0#システムサウンドのチャンネル番号
player_animations={
    "normal":(0,24,0,8,8,11),#イメージバンク番号,x,y,幅,高さ,透明扱いの色(ないなら空白)
    "right" :(0,32,0,8,8,11),
    "left"  :(0,24,8,8,8,11),
    "up"    :(0,24,0,8,8,11),
    "down"  :(0,24,0,8,8,11),
    "damage":(0,32,8,8,8,11),
        }
character_particles={
    "plus":(0,8,16,8,8,0),
    "minus":(0,16,16,8,8,0),
}
enemy_cost_list={
    "level_1":(0,40,0,12,12,11),
    "level_2":(0,52,0,12,12,11),
    "level_3":(0,64,0,12,12,11)
            }
enemy_w,enemy_h=12,12
items_cost={
    "healing":(0,48,16,8,8,0),
    "fire_rate_up":(0,56,16,8,8,0)
}
hp_cost_list={
    "empty" :(0,24,16,8,8,11),
    "normal":(0,32,16,8,8,11),
    "extra" :(0,40,16,8,8,11),
}
hp_max=3
extra_hp_max=6
extra_heart_time=250#エクストラHPの寿命(フレーム)
healing_probability=10#回復アイテム出現確率
sound_list={
    "None":(system_sound_ch,0),
    "not":(system_sound_ch,6),
    "select":(system_sound_ch,7),
    "bang":(character_se_ch,1),
    "dash":(character_se_ch,9,),
    "boom":(character_se_ch,2),
    "hit":(system_sound_ch,3),
    "del_extra":(system_sound_ch,10),
    "healing_get":(system_sound_ch,8),
    "decide":(system_sound_ch,4),
    "game_over":(system_sound_ch,5)
}
#--------------------------------

#----------スプライト----------
class base_sprite:
    def __init__(self,x,y,w=8,h=8,life=1):
        """コンストラクタ"""
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.life=life#HP
        self.vx,self.vy=0,0
    def update(self):
        """更新処理"""
    def draw(self):
        """描画(派生クラスで実装)"""

class item_sprite(base_sprite):
    def __init__(self,name, x, y, w=8, h=8, life=1):
        super().__init__(x, y, w, h, life)
        self.name=name
        self.vx=0
        self.vy=1
    def update(self):
        """更新処理"""
        self.x+=self.vx
        self.y+=self.vy
        if not( (0<self.x+self.w<W) and (0<self.y<H) ):
            self.life=0
    def draw(self):
        """描画処理"""
        pyxel.blt(self.x,self.y,*items_cost[self.name])

class snow_particle(base_sprite):#スノーパーティクル
    def __init__(self, x, y):
        super().__init__(x, y,1,1)
        self.vy=random.randint(2,8)/10
    def update(self):
        self.x+=self.vx;self.y+=self.vy
        if self.y > H:self.y=0
    def draw(self):
        pyxel.rect(self.x, self.y, 1, 1, 7)

class bomb_particle(base_sprite):#爆発パーティクル
    def __init__(self, x, y, size,col=10):
        super().__init__(x, y, size,size)
        pyxel.play(*sound_list["boom"])
        self.l_size=size#最終サイズ
        self.n_size=0#現在サイズ
        self.col=col#色指定
    def draw(self):
        """描画処理"""
        pyxel.circ(self.x,self.y,self.n_size,self.col)
    def update(self):
        """更新処理"""
        if self.l_size <= self.n_size : self.life=0
        else:self.n_size+=1

class character_particle(base_sprite):
    def __init__(self,particle_name="plus" , character=object, w=8, h=8, life=1):
        super().__init__(character.x, character.y+8, w, h, life)
        self.name=particle_name
        self.character=character
        if self.name=="plus":self.gap=8
        if self.name=="minus":self.gap=-8
        self.blt_x = self.character.x#描画位置
        self.blt_y = self.character.y + self.gap
        self.x = 0
        self.y = self.gap #キャラクターの位置からの相対座標
    def draw(self):
        pyxel.blt(self.blt_x,self.blt_y,*character_particles[self.name])
    def update(self):
        if self.name =="plus":
            if -5 >= self.y : self.life=0
            else:self.y -= 1.5
            self.blt_x = self.character.x+self.x #描画位置
            self.blt_y = self.character.y+self.y
        if self.name =="minus":
            if 5 <= self.y : self.life=0
            else:self.y += 1.5
            self.blt_x = self.character.x+self.x #描画位置
            self.blt_y = self.character.y+self.y
    
class heart_sprite(base_sprite):
    def __init__(self, x=5, y=3, w=8, h=8,hp=0,cost="normal"):
        super().__init__(x, y, w, h, life=1)
        self.player_hp=hp
        self.cost=cost
    def draw(self):
        """描画処理"""
        pyxel.blt(self.x,self.y,*hp_cost_list[self.cost])
    def update(self):
        pass

class player_sprite(base_sprite):
    def __init__(self, x, y,speed,bullet,bomb,life):
        """コンストラクタ"""
        super().__init__(x, y,8,8,life)#親クラスのコンストラクタ(座標二つ,幅と高さ)
        self.cost="normal"
        self.speed=speed
        self.bullets=bullet
        self.fire_rate_count=0
        self.fire_rate=fire_rate_frame
        self.dash_freeze_count=0
        self.bomb=bomb
        #コスチューム用意
        self.cost_list=player_animations
    def update(self):
        """更新処理"""
        self.move_control()
        self.fire_control()
        self.dash_control()
        self.x+=self.vx;self.y+=self.vy
    def draw(self):
        """描画処理"""
        pyxel.blt(self.x,self.y,*self.cost_list[self.cost])
    def move_control(self):
        if ( (pyxel.btn(pyxel.KEY_A) and (pyxel.btn(pyxel.KEY_D) ) ) ) or ( pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) and pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) ) :
            self.vx=0
        elif ( (pyxel.btn(pyxel.KEY_A) and not(pyxel.btn(pyxel.KEY_D) ) ) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) ) and 0<self.x+(self.w/2):
            if not self.cost=="damage":self.cost="left"
            self.vx=-1*self.speed
        elif ( pyxel.btn(pyxel.KEY_D) and not pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) ) and self.x+self.w/2 < W:
            if not self.cost=="damage":self.cost="right"
            self.vx=self.speed
        else:
            if not self.cost=="damage":self.cost="normal"
            self.vx=0
        
        if ( (pyxel.btn(pyxel.KEY_W) and (pyxel.btn(pyxel.KEY_S) ) ) ) or ( pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) and pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) ) :
            self.vy=0    
        elif ( pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) ) and 0<self.y+(self.h/2):
            if not(self.cost=="right" or self.cost=="left" or self.cost=="damage"):self.cost="up"
            self.vy=-1*self.speed
        elif ( pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) ) and (self.y+self.h/2) < H:
            if not(self.cost=="right" or self.cost=="left" or self.cost=="damage"):self.cost="down"
            self.vy=self.speed
        else:
            self.vy=0
        
        if not(
            pyxel.btn(pyxel.KEY_A)or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) 
            ) and not(
                pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            ) and not(
                pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) 
            ) and not(
                pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) ):#ニュートラル
            pass
            #self.cost="normal"
    def fire_control(self):
        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_X)):#スペースキー
            if (game_frame_count > self.fire_rate+self.fire_rate_count):#前回発射から発射硬直以上
                self.bullets.append(bullet_sprite(self.x,self.y,2,6,cost=self.cost,speed=bullet_speed,bomb=self.bomb))
                self.fire_rate_count=game_frame_count
    def dash_control(self):
        if pyxel.btn(pyxel.KEY_B) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            if (game_frame_count > dash_freeze_frame+self.dash_freeze_count):#ダッシュ
                pyxel.play(*sound_list["dash"])
                self.x+=self.vx*2
                self.y+=self.vy*2
                self.dash_freeze_count=game_frame_count
            else:
                pass
        if self.dash_freeze_count+dash_frame > game_frame_count:#ダッシュ継続時間ならスピードアップのまま
            self.x+=self.vx*2
            self.y+=self.vy*2
        
class enemy(base_sprite):
    def __init__(self, x, y,life,level="level_1"):
        """コンストラクタ"""
        super().__init__(x, y,enemy_w,enemy_h,life)#親クラスのコンストラクタ(座標二つ,幅と高さ)
        self.vx=0
        self.vy=0
        self.angle=0
        self.center_x=x+5
        self.center_y=y+5
        self.trandition=1
        self.cost=level
        self.a_frame=-30#前回の移動初めのフレ
    def update(self):
        """更新処理"""
        self.move_control()
        self.x+=self.vx;self.y+=self.vy
    def draw(self):
        """描画処理"""
        pyxel.blt(self.x,self.y,*enemy_cost_list[self.cost])

    def move_control(self):
        if self.cost=="level_1":
            self.level_1_move()
        elif self.cost=="level_2":
            self.level_2_move()
        elif self.cost=="level_3":
            self.level_3_move()
        else: self.level_0_move()

    def enemy_control_base(self):#画面外防止
        if 0>self.x+self.vx:self.vx=1#左に行きすぎたら強制的に右へ
        elif self.x+self.vx > W:self.vx=-1#上の逆
        if 0 > self.y+self.vy:self.vy=1#上に行きすぎたら強制的に下へ
        elif self.y+self.vy > H:self.vy=-1#上の逆
    def level_0_move(self):
        self.vx,self.vy=0,0
    def level_1_move(self):
        self.enemy_control_base()
        if game_frame_count > self.a_frame+30:
            self.trandition=random.randint(0,1)
            if self.trandition == 0:
                self.vx=random.uniform(-2,2)
                self.vy=0
            elif self.trandition == 1:
                self.vx=0
                self.vy=random.uniform(-2,2)
            self.a_frame = game_frame_count
    def level_2_move(self):
        self.enemy_control_base()
        if game_frame_count > self.a_frame+30:
            self.vx=random.uniform(-1.5,1.5)
            self.vy=random.uniform(-1.5,1.5)
            self.a_frame = game_frame_count
    def level_3_move(self):
        self.speed=6#速度
        self.move_r=25#半径
        
        if game_frame_count >= self.a_frame+31:
            self.trandition=random.randint(1,8)#1(3時→12時→9時),2(9時→12時→3時),3(3時→6時→9時),4(9時→6時→3時),5(6時→9時→12時),6(6時→3時→12時),7(12時→9時→6時),8(12時→3時→6時)
            if 0>self.x:self.trandition=4#左に行きすぎたら強制的に右へ
            elif self.x> W:self.trandition=1#上の逆
            elif 0 > self.y:self.trandition=8#上に行きすぎたら強制的に下へ
            elif self.y > H:self.trandition=6#上の逆

            if self.trandition==1 or self.trandition==3 : self.angle=0 ; self.center_x=self.x-self.move_r ; self.center_y=self.y#中心を左側へ
            elif self.trandition==2 or self.trandition==4 : self.angle=0 ; self.center_x=self.x+self.move_r ; self.center_y=self.y#中心を右側へ
            elif self.trandition==5 or self.trandition==6 : self.angle=0 ; self.center_x=self.x ; self.center_y=self.y-self.move_r#中心を上側へ
            elif self.trandition==7 or self.trandition==8 : self.angle=0 ; self.center_x=self.x;self.center_y=self.y+self.move_r#中心を下側へ
            self.a_frame=game_frame_count
        else:
            if self.trandition == 1:
                self.angle-=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.cos(self.rad) * self.move_r
                self.y = self.center_y + math.sin(self.rad) * self.move_r
            elif self.trandition == 2:
                self.angle+=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.cos(self.rad) * -self.move_r
                self.y = self.center_y + math.sin(self.rad) * -self.move_r
            elif self.trandition == 3:
                self.angle-=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.cos(self.rad) * self.move_r
                self.y = self.center_y + math.sin(self.rad) * -self.move_r
            elif self.trandition == 4:
                self.angle+=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.cos(self.rad) * -self.move_r
                self.y = self.center_y + math.sin(self.rad) * self.move_r
            elif self.trandition == 5:
                self.angle-=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.sin(self.rad) * self.move_r
                self.y = self.center_y + math.cos(self.rad) * self.move_r
            elif self.trandition == 6:
                self.angle+=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.sin(self.rad) * self.move_r
                self.y = self.center_y + math.cos(self.rad) * self.move_r
            elif self.trandition == 7:
                self.angle+=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.sin(self.rad) * -self.move_r
                self.y = self.center_y + math.cos(self.rad) * -self.move_r
            elif self.trandition == 8:
                self.angle-=self.speed
                self.rad = math.radians(self.angle)
                self.x = self.center_x + math.sin(self.rad) * -self.move_r
                self.y = self.center_y + math.cos(self.rad) * -self.move_r

class bullet_sprite(base_sprite):
    def __init__(self, x, y,w=2,h=6,cost="normal",speed=1,bomb=[]):
        super().__init__(x, y,w,h)
        self.angle=cost
        self.speed=speed;self.w=w;self.h=h
        self.x=x+3;self.y=y
        self.bomb=bomb
        pyxel.play(*sound_list["bang"])
    def update(self):
        """更新処理"""
        self.move()
        self.life_flag()
    def draw(self):
        """描画処理"""
        pyxel.rect(self.x,self.y,self.w,self.h,9)
        #属性によって玉の向きを変える
        #if self.angle=="up"or self.angle=="down":pyxel.rect(self.x,self.y,self.w,self.h,9)
        #else:pyxel.rect(self.x,self.y,self.w,self.h,9)
    def move(self):
        self.y-=self.speed
        #属性によって進む向きを変える
        #if self.angle=="up":self.y-=speed
        #elif self.angle=="down":self.y+=speed
        #elif self.angle=="right":self.x+=speed
        #elif self.angle=="left":self.x-=speed
    def life_flag(self):
       #画面内かどうか判定
       if not( (-10<self.x+self.w<W+10) and (-10<self.y<H+10) ):
           self.life=0
       #elif (enemy.x < self.x < enemy.x+7) and (enemy.y < self.y < enemy.y+8):
        #   self.life=0;self.bomb.append(bomb_particle(self.x,self.y,4))
       #else : self.life=1 

#------------------------------

class Game:
    def __init__(self):
        """コンストラクタ"""
        #pyxel起動
        pyxel.init(W,H,title="shooter")#リセット
        #width(幅),height(高さ),title(タイトルバーの名前),fps(フレームレート),quit_key(閉じるキー指定),display_scale(表示倍率),capture_scale(録画の画質),capture_sec(録画最大秒数)
        pyxel.load("shooter_resource.pyxres")#ソースファイル読み込み
        # ローカルロード------
        self.bullets=[]#弾リスト
        self.bomb=[]#爆発パーティクルリスト
        self.enemy_list=[]#敵リスト
        self.snow_list = [#スノーパーティクルを50個生成
        snow_particle(random.randint(0, W), random.randint(0, H)) for _ in range(50)
        ]
        self.items_list=[]#アイテムリスト
        self.fire_rate_up_time=0
        self.heart_list=[]
        self.player_particles_list=[]#パーティクルリスト
        self.heart_del_frame=0
        self.now_stage="stage_1"
        self.start_menu_call()
        self.hit_frame=game_frame_count
        self.score=0
        self. high_score=0#ロード時に削除
        pyxel.run(self.update,self.draw)#実行関数(デフォルト毎秒30回)
    def update(self):
        """更新処理"""
        if self.screen_status=="start_menu":
            self.start_menu_update()
        elif self.screen_status == "play":
            self.play_update()
            #print(self.player.life)
        elif self.screen_status =="traning":
            self.traning_update()
        elif self.screen_status =="pose":
            self.pose_update()
        elif self.screen_status == "ranking":
            self.ranking_update()
        elif self.screen_status=="result":
            self.result_update()  
    def draw(self):
        """描画処理"""
        pyxel.cls(0)#clear screen(画面の内容を消す)
        if self.screen_status == "start_menu" :#start menu
            self.start_menu_draw()
        elif self.screen_status == "play" :#play
            self.play_draw()
        elif self.screen_status == "traning":
            self.traning_draw()
        elif self.screen_status =="pose":
            self.pose_draw()
        elif self.screen_status == "ranking":
            self.ranking_draw()
        elif self.screen_status == "result":#result
            self.result_draw()

    def jadge_hit(self):
        """当たり判定"""
        for e in self.enemy_list: 
            #敵と弾の当たり判定
            for b in self.bullets:
                if (e.x <= b.x+1 and b.x < e.x+enemy_w) and (e.y < b.y < e.y+enemy_h):
                    b.life += -1
                    e.life += -1
                    self.score+=1
                    if e.life > 0:pyxel.play(*sound_list["hit"])
            #敵とplayerの当たり判定
            if self.player.life > 0:
                #当たったフレームと無敵時間足した時<今のフレーム数
                if self.hit_frame+invincible_frame < game_frame_count and (e.x+3 < self.player.x < e.x+8 or e.x+3 < self.player.x+7 < e.x+8) and (e.y < self.player.y < e.y+10 or e.y < self.player.y+7 < e.y+10):
                    self.player.life+= -1
                    pyxel.play(*sound_list["hit"])
                    self.hit_frame=game_frame_count
                elif self.hit_frame+invincible_frame > game_frame_count:
                    self.player.cost="damage"
                else:
                    self.player.cost="normal"
            #playerとアイテムの当たり判定
        for i in self.items_list:
            if (i.x < self.player.x < i.x+7 or i.x < self.player.x+7 < i.x+7) and (i.y < self.player.y < i.y+7 or i.y < self.player.y+7 < i.y+7):
                i.life=0
                if i.name=="healing":
                    pyxel.play(*sound_list["healing_get"])
                    self.player_particles_list.extend([character_particle("plus",self.player)])
                    if self.player.life < extra_hp_max : self.player.life+=1
                    self.heart_del_frame = game_frame_count
                elif i.name=="fire_rate_up":
                    pyxel.play(*sound_list["healing_get"])
                    self.player_particles_list.extend([character_particle("plus",self.player)])
                    self.player.fire_rate=3
                    self.fire_rate_up_time=game_frame_count#連射速度アップ時間に今の時間を代入

    def jadge_life(self):#弾の削除、爆発パーティクル、敵とアイテムの生成、削除
        """生存判定"""
        self.bullets[:] = [b for b in self.bullets if b.life > 0]#bulletsの中身を全部一つずつ取り出してlifeが1のインスタンスを抽出して入れ直す
        self.bomb.extend([bomb_particle(e.x,e.y,6) for e in self.enemy_list if e.life <= 0]) #敵のHPがゼロになった時爆発パーティクル追加
        #アイテム生成
        for e in self.enemy_list :
            if e.life <= 0:
                prob = item_probability_list
                p1 = prob["None"]
                p2 = p1 + prob["healing"]
                p3 = p2 + prob["fire_rate_up"]
                self.item_probability=random.randint(1,100)
                if 0 < self.item_probability <= p1:
                    pass
                elif p1 < self.item_probability <= p2 :
                    self.items_list.extend([item_sprite("healing",e.x,e.y)]) 
                elif p2 < self.item_probability  <= p3 :
                    self.items_list.extend([item_sprite("fire_rate_up",e.x,e.y)])
        
        self.bomb[:] = [b for b in self.bomb if b.life > 0]#爆発パーティクル生存判定
        self.enemy_list[:] = [e for e in self.enemy_list if e.life > 0]#敵生存判定
        self.items_list[:] = [i for i in self.items_list if i.life > 0]#アイテムの生存判定
        self.player_particles_list[:] = [p for p in self.player_particles_list if p.life > 0]
        while len(self.enemy_list) > enemy_stage_level_list[self.now_stage]["enemy_max"]:#敵が多すぎたら削除
             self.enemy_list.pop(0) 
        while len(self.enemy_list) < enemy_stage_level_list[self.now_stage]["enemy_max"]:
            # 現在のステージの確率データを取得する
            prob = enemy_stage_level_list[self.now_stage]
            p1 = prob["level_1"]
            p2 = p1 + prob["level_2"]
            p3 = p2 + prob["level_3"]
            self.enemy_probability = random.randint(1, 100)
            if 0 < self.enemy_probability <= p1:
                self.enemy_list.append(enemy(random.randint(0, W), H/4, 1, "level_1"))
            elif p1 < self.enemy_probability <= p2:
                self.enemy_list.append(enemy(random.randint(0, W), H/4, 1, "level_2"))
            elif p2 < self.enemy_probability <= p3:
                self.enemy_list.append(enemy(random.randint(0, W), H/4, 1, "level_3"))
    def player_create(self):
        self.player=player_sprite(W/2,100,speed=player_speed,bullet=self.bullets,bomb=self.bomb,life=hp_max)#プレイヤー生成
        self.score=0
        self.hit_frame=game_frame_count


    def start_menu_update(self):#スタートメニューの画面更新処理
        for s in self.snow_list: s.update()#スノーパーティクルのアップデート処理
        for b in self.bullets: b.update()#弾の更新処理
        for b in self.bomb:b.update()#爆発パーティクル更新処理
        for e in self.enemy_list: e.update()#敵更新処理
        
        if self.menu_selected_option == "play":self.menu_next_option="traning_mode"
        if self.menu_selected_option == "traning_mode":self.menu_next_option="online_ranking"
        if self.menu_selected_option == "online_ranking":self.menu_next_option="play"

        self.jadge_life()
        if ( pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) ):
            pyxel.play(*sound_list["None"])
            pyxel.play(*sound_list["decide"])
            if self.menu_selected_option=="play":
                # playにカーソルがあってスペースキーが押されたらプレイヤーを生成してプレイ状態(1)へ
                self.play_call()
            elif self.menu_selected_option=="traning_mode":
                # traningにカーソルがあってスペースキーが押されたらトレーニングモードへ
                self.traning_call()
            elif self.menu_selected_option=="online_ranking":
                #online rankingにカーソルがあってスペースキーが押されたならランキングへ
                #今は音鳴らすだけ
                pyxel.play(*sound_list["not"])
                #self.screen_status="ranking"
                #enemy_stage_level_list[self.now_stage]["enemy_max"]=0
        if (pyxel.btnp(pyxel.KEY_RSHIFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK)):
            pyxel.play(*sound_list["select"])
            self.menu_selected_option=self.menu_next_option
    def start_menu_draw(self):#スタートメニューの描画処理
        for s in self.snow_list: s.draw()##スノーパーティクルの描画処理
        for b in self.bomb: b.draw()#爆発パーティクルの描画処理
        for e in self.enemy_list : e.draw()#敵の描画処理

        pyxel.text(10,10,f"HIGH SCORE:{self.high_score}",14)
        self.draw_text(W/2,H/2-24,"SHOOTER",6)
        self.draw_text(W/2,H/2,"PLAY",14)
        self.draw_text(W/2,H/2+12,"TRAINING MODE",14)
        self.draw_text(W/2,H/2+24,"COMING SOON",14)
        if self.menu_selected_option == "play" : self.draw_text(W/2,H/2,"PLAY",8)
        if self.menu_selected_option =="traning_mode" :self.draw_text(W/2,H/2+12,"TRAINING MODE",8)
        if self.menu_selected_option == "online_ranking" : self.draw_text(W/2,H/2+24,"COMING SOON",8)
        #pyxel.text(W/2,H/2+10,"©koudai",14)
    def start_menu_call(self):
        self.screen_status = "start_menu"
        self.menu_selected_option="play"
        self.now_stage="stage_0"

    def play_update(self):#プレイ画面の画面更新処理 パーティクル,弾,敵,プレイヤーの更新　ポーズ判定
        global game_frame_count
        game_frame_count+=1
        for s in self.snow_list: s.update()#スノーパーティクルのアップデート処理
        for b in self.bullets: b.update()#弾の更新処理
        for b in self.bomb:b.update()#爆発パーティクル更新処理
        for e in self.enemy_list: e.update()#敵更新処理
        for i in self.items_list: i.update()#アイテムアップデート
        for p in self.player_particles_list: p.update()
        if  0 <= self.score < 50:self.now_stage="stage_1"
        elif 50 <= self.score < 100:self.now_stage="stage_2"
        elif 100 <= self.score < 150:self.now_stage="stage_3"
        elif 150 <= self.score < 200:self.now_stage="stage_4"
        elif 200 <= self.score:self.now_stage="stage_5"
        #ハートの削除判定
        if self.player.life > hp_max:
            if game_frame_count > self.heart_del_frame + extra_heart_time:
                pyxel.play(*sound_list["del_extra"])
                self.player_particles_list.extend([character_particle("minus",self.player)])
                self.player.life -= 1
                self.heart_del_frame = game_frame_count
        #ハートリストの更新
        self.heart_list=[
            heart_sprite(x=5+i*9,y=5,cost="empty") for i in range(hp_max)
            ]+[
            heart_sprite(x=5+i*9,y=5,cost="normal") for i in range( min(self.player.life,hp_max) )#min(x,y)は双方の値の小さいほうを返す
            ]+[
            heart_sprite(x=5+hp_max*9+i*9,y=5,cost="extra")for i in range(self.player.life-hp_max)
            ]
        #最後尾のハートの点滅
        if self.heart_list[-1].cost=="extra":
            if self.heart_del_frame+extra_heart_time > game_frame_count > self.heart_del_frame+extra_heart_time-100:
                if 0 <= game_frame_count%50 <= 49:
                    self.heart_list[-1].cost="empty"
                    if 0 <= game_frame_count%60 <= 35 :
                        self.heart_list[-1].cost="extra"
        #連射速度アップの終了判定
        if self.player.fire_rate < fire_rate_frame and self.fire_rate_up_time+fire_rate_up_time < game_frame_count:
            self.player_particles_list.extend([character_particle("minus",self.player)])
            pyxel.play(*sound_list["del_extra"])
            self.player.fire_rate=fire_rate_frame
            
        #プレイヤーのアップデートと爆殺処理
        if self.player.life<=0:
            #lifeがゼロになったら爆殺してリザルト画面へ 
            self.bomb.extend([bomb_particle(self.player.x,self.player.y,20,8)])
            self.player.life+=-1
            self.result_call()
        elif self.player.life > 0: 
            self.player.update()
        else: pass
        if self.player.life > extra_hp_max :
            self.player.life = extra_hp_max

        self.jadge_life()
        self.jadge_hit()
        if self.score > self.high_score : self.high_score=self.score
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):#ポーズメニュー
            pyxel.play(*sound_list["decide"])
            self.pose_call()
    def play_draw(self):#プレイ画面の描画処理
        for s in self.snow_list: s.draw()##スノーパーティクルの描画処理
        for b in self.bullets: b.draw()#弾の描画処理
        for b in self.bomb: b.draw()#爆発パーティクルの描画処理
        for e in self.enemy_list : e.draw()#敵の描画処理
        for i in self.items_list : i.draw()#アイテムの描画処理
        for h in self.heart_list : h.draw()
        for p in self.player_particles_list : p.draw()#パーティクル描画
        self.player.draw()
        pyxel.rectb(5 , 15 ,dash_freeze_frame , 8 , 10)
        pyxel.rect(5 , 15 , dash_freeze_frame-(game_frame_count-self.player.dash_freeze_count) , 8 , 10)
        pyxel.text(5,30,f"SCORE:{self.score}",14)
        pyxel.text(5,38,f"HIGH SCORE:{self.high_score}",14)
    def play_call(self):
        self.screen_status = "play"
        self.heart_list=[heart_sprite(cost="normal") for _ in range(hp_max)]
        self.items_list=[]
        self.player_create()

    def pose_update(self):#ポーズ画面の画面更新処理
        if self.menu_selected_option == "return":self.menu_next_option="escape"
        if self.menu_selected_option == "escape":self.menu_next_option="return"
        if ( pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) ):
            pyxel.play(*sound_list["None"])
            pyxel.play(*sound_list["decide"])
            if self.menu_selected_option=="return":
                # returnにカーソルがあってスペースキーが押されたらプレイ状態(1)へ
                self.screen_status = "play"
            elif self.menu_selected_option=="escape":
                # escapeにカーソルがあってスペースキーが押されたらメニューへ
                self.start_menu_call()
        if (pyxel.btnp(pyxel.KEY_RSHIFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK)):
            pyxel.play(*sound_list["select"])
            self.menu_selected_option = self.menu_next_option
    def pose_draw(self):#ポーズ画面の画面描画処理
        self.play_draw()
        self.draw_text(W/2,H/2-24,"PAUSE",6)
        self.draw_text(W/2,H/2+12,"RETURN",14)
        self.draw_text(W/2,H/2+24,"ESCAPE",14)
        if self.menu_selected_option == "return" : self.draw_text(W/2,H/2+12,"RETURN",8)
        if self.menu_selected_option =="escape" :self.draw_text(W/2,H/2+24,"ESCAPE",8)
    def pose_call(self):
        self.screen_status="pose"        
        self.menu_selected_option="return"
        self.menu_next_option="escape"

    def traning_update(self):#トレーニングモードの画面更新処理
        self.play_update()      
    def traning_draw(self):#トレーニングモードの描画処理
        for s in self.snow_list: s.draw()##スノーパーティクルの描画処理
        for b in self.bullets: b.draw()#弾の描画処理
        for b in self.bomb: b.draw()#爆発パーティクルの描画処理
        for e in self.enemy_list : e.draw()#敵の描画処理

        self.play_draw()
    def traning_call(self):
        self.now_stage="stage_0"
        self.items_list=[]
        self.screen_status = "traning"
        self.player_create()

    def ranking_update(self):#ランキングの画面更新処理
        for s in self.snow_list: s.update()#スノーパーティクルのアップデート処理
        for b in self.bullets: b.update()#弾の更新処理
        for b in self.bomb:b.update()#爆発パーティクル更新処理
        for e in self.enemy_list : e.draw()#敵の描画処理
    def ranking_draw(self):#ランキングの描画処理
        for s in self.snow_list: s.draw()##スノーパーティクルの描画処理
        for b in self.bullets: b.draw()#弾の描画処理
        for b in self.bomb: b.draw()#爆発パーティクルの描画処理
        for e in self.enemy_list : e.draw()#敵の描画処理
    def ranking_call(self):#ここでオンラインデータを読み込んだうえでランキングを呼び出す
        pass
    
    def result_update(self):#リザルトの画面更新処理
        for s in self.snow_list: s.update()#スノーパーティクルのアップデート処理
        for b in self.bullets: b.update()#弾の更新処理
        for b in self.bomb:b.update()#爆発パーティクル更新処理
        for e in self.enemy_list: e.update()#敵更新処理

        self.jadge_life()
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) :
            pyxel.play(*sound_list["decide"])
            self.start_menu_call()
    def result_draw(self):#リザルトの描画処理
        for s in self.snow_list: s.draw()##スノーパーティクルの描画処理
        for b in self.bullets: b.draw()#弾の描画処理
        for b in self.bomb: b.draw()#爆発パーティクルの描画処理
        for e in self.enemy_list : e.draw()#敵の描画処理
        self.draw_text(W/2,H/2-14,"GAME OVER",14)
        self.draw_text(W/2,H/2,f"SCORE:{self.score}",14)
        self.draw_text(W/2,H/2+10,(f"HIGH SCORE:{self.high_score}"),14)
    def result_call(self):
        self.screen_status="result"
        #サーバーへ送信後セーブ
        pyxel.play(*sound_list["game_over"])
    def draw_text(self,x=W/2,y=H/2,text="text",col=14):#真ん中でテキスト描画
        pyxel.text (x-2*len(text) , y-3, text , col )

def main():
    """メイン処理"""
    Game()

if __name__ == "__main__":
    main()