"""
 ______  ______   __   __   ______   __  __   ______    
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\   
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\   
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\ 
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/ 
                                   

Changelog :

v0.6 Fixed crash on ER, Improved Q positioning, Reduced lags

v0.7 Now use Ponche Pred

v0.8 Added some smalls imporvements

v0.85 Adapted script to new pred API

v0.9 Fixed some bugs

v0.95 Made compatible with pred changes

v0.96 Fixed crash in QR hitcount calculation

"""

from valkyrie import *
from PO_Prediction import *
import math
from helpers.flags import Orbwalker
from helpers.targeting import TargetSelector, TargetSet

target_selector = TargetSelector(0, TargetSet.Champion)

q_combo = True
q_combo_hitchance = HitChance.Medium
w_combo = True
w_auto = True
e_combo = True
e_combo_dmg = True
r_combo = True
r_auto = False
qr = True
qr_hitchance = HitChance.Medium
er = True

q_range = 815
q_speed = 1200
q_delay = 0.25
q_width = 80

w_width = 210
w_delay = 0.25

e_speed = 1850
e_range = 1095
e_delay = 0.25
e_width = 80

ball_position = None
ball_moving = False

ball_draw = True
ball_max_range = 1250

r_width = 380
r_delay = 0.5
r_value = 2

fight_range = 2000
include_clones = False

ball_draw_angle = 360


def valkyrie_menu(ctx: Context):
    global qr_hitchance, q_combo_hitchance, e_combo_dmg, include_clones, w_auto, r_auto, ball_draw, qr, er, q_combo, w_combo, e_combo, r_combo, q_angle_step, q_delay, q_width, w_width, w_delay, e_delay, e_width, r_width, r_delay, r_value
    ui = ctx.ui

    ui.text("Ponche Orianna V0.96")
    ui.separator()
    include_clones = ui.checkbox('Include clones', include_clones)
    ui.help("Training dummy are considered as clones")
    ui.separator()
    if ui.beginmenu("Draw"):
        ball_draw = ui.checkbox('Ball', ball_draw)
        ui.endmenu()
    ui.separator()
    if ui.beginmenu("Q"):
        q_combo = ui.checkbox('Q - Combo', q_combo)
        q_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(q_combo_hitchance), q_combo_hitchance, 2)
        ui.separator()
        q_delay = ui.sliderfloat("Activation delay", q_delay, 0.0, 1.0)
        q_width = ui.sliderint("Hitbox size", q_width, 0, 80)
        ui.endmenu()
    ui.separator()
    if ui.beginmenu("W"):
        w_combo = ui.checkbox('W - Combo', w_combo)
        w_auto = ui.checkbox('W - Auto', w_auto)
        ui.separator()
        w_delay = ui.sliderfloat("Activation delay", w_delay, 0.0, 1.0)
        w_width = ui.sliderint("Hitbox size", w_width, 0, 230)
        ui.endmenu()
    ui.separator()
    if ui.beginmenu("E"):
        e_combo = ui.checkbox('E - Combo', e_combo)
        ui.separator()
        e_combo_dmg = ui.checkbox('E to deal Dmg', e_combo_dmg)
        e_delay = ui.sliderfloat("Activation delay", e_delay, 0.0, 1.0)
        e_width = ui.sliderint("Hitbox size", e_width, 0, 80)
        ui.endmenu()
    ui.separator()
    if ui.beginmenu("R"):
        r_combo = ui.checkbox('R - Combo', r_combo)
        r_auto = ui.checkbox('R - Auto', r_auto)
        ui.help('Use R even out of combo mode')
        ui.separator()
        qr = ui.checkbox('QR - Use', qr)
        qr_hitchance = ui.sliderenum(
            "QR - Hit Chance", HitChance.GetHitChanceName(qr_hitchance), qr_hitchance, 2)
        er = ui.checkbox('ER - Use', er)
        ui.separator()
        r_delay = ui.sliderfloat("Activation delay", r_delay, 0.0, 1.0)
        r_width = ui.sliderint("Hitbox size", r_width, 0, 410)
        ui.separator()
        r_value = ui.sliderint("Min hit count", r_value, 1, 5)
        ui.help("Minimum number of enemies to cast R")
        ui.endmenu()
    ui.separator()


def valkyrie_on_load(ctx: Context):
    global qr_hitchance, q_combo_hitchance, e_combo_dmg, include_clones, w_auto, r_auto, ball_draw, qr, er, q_combo, w_combo, e_combo, r_combo, q_angle_step, q_delay, q_width, w_width, w_delay, e_delay, e_width, r_width, r_delay, r_value

    cfg = ctx.cfg

    include_clones = cfg.get_bool('include_clones', include_clones)
    ball_draw = cfg.get_bool('ball_draw', ball_draw)

    q_combo = cfg.get_bool('q_combo', q_combo)
    q_combo_hitchance = cfg.get_int('q_combo_hitchance', q_combo_hitchance)
    w_combo = cfg.get_bool('w_combo', w_combo)
    w_auto = cfg.get_bool('w_auto', w_auto)
    e_combo = cfg.get_bool('e_combo', e_combo)
    e_combo_dmg = cfg.get_bool('e_combo_dmg', e_combo_dmg)
    r_combo = cfg.get_bool('r_combo', r_combo)
    r_auto = cfg.get_bool('r_auto', r_auto)
    qr = cfg.get_bool('qr', qr)
    qr_hitchance = cfg.get_int('qr_hitchance', qr_hitchance)
    er = cfg.get_bool('er', er)

    q_delay = cfg.get_float('q_delay', q_delay)
    q_width = cfg.get_int('po_ori_q_width', q_width)

    w_delay = cfg.get_float('w_delay', w_delay)
    w_width = cfg.get_int('w_width', w_width)

    e_delay = cfg.get_float('e_delay', e_delay)
    e_width = cfg.get_int('e_width', e_width)

    r_width = cfg.get_int('r_width', r_width)
    r_delay = cfg.get_float('r_delay', r_delay)
    r_value = cfg.get_int('r_value', r_value)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('include_clones', include_clones)
    cfg.set_bool('ball_draw', ball_draw)

    cfg.set_bool('q_combo', q_combo)
    cfg.set_int('q_combo_hitchance', q_combo_hitchance)
    cfg.set_bool('w_combo', w_combo)
    cfg.set_bool('w_auto', w_auto)
    cfg.set_bool('e_combo', e_combo)
    cfg.set_bool('e_combo_dmg', e_combo_dmg)
    cfg.set_bool('r_combo', r_combo)
    cfg.set_bool('r_auto', r_auto)
    cfg.set_bool('qr', qr)
    cfg.set_int('qr_hitchance', qr_hitchance)
    cfg.set_bool('er', er)

    cfg.set_float('q_delay', q_delay)
    cfg.set_int('q_width', q_width)

    cfg.set_float('w_delay', w_delay)
    cfg.set_int('w_width', w_width)

    cfg.set_float('e_delay', e_delay)
    cfg.set_int('e_width', e_width)

    cfg.set_int('r_width', r_width)
    cfg.set_float('r_delay', r_delay)
    cfg.set_int('r_value', r_value)


def er_hitcount(player: ChampionObj, e_spell: SpellObj, enemies: list[ChampionObj], allies: list[ChampionObj]):
    if not player.can_cast_spell(e_spell) or not er or len(allies) == 0:
        return 0, None

    best_hitcount = 0
    best_ally = None
    best_distance_overall = 0
    for ally in allies:
        distance = ball_position.distance(ally.pos)
        delay_reach = distance / e_speed + e_delay
        ally_position = Utility.To2D(ally.predict_position(delay_reach))
        hitcount = 0
        distance_overall = 0
        for enemy in enemies:
            enemy_position = Utility.To2D(enemy.predict_position(delay_reach))
            distance_to_enemy = ally_position.distance(enemy_position)
            if distance_to_enemy < r_width:
                distance_overall += math.exp(distance_to_enemy)
                hitcount += 1
        if hitcount > best_hitcount or (hitcount == best_hitcount and best_distance_overall > distance_overall):
            best_ally = ally
            best_hitcount = hitcount

    return best_hitcount, best_ally


def qr_hitcount(player: ChampionObj, q_spell: SpellObj, enemies: list[ChampionObj]):
    if False or not player.can_cast_spell(q_spell) or not qr:
        return 0, None

    bestCount = 0
    bestPos = None
    for enemy in enemies:
        input = PredictionInput(enemy, ball_position.clone(), player.pos.clone(
        ), False, delay=q_delay, radius=r_width, speed=q_speed, range=q_range, type=SkillshotType.SkillshotCircle, collision=False)
        output = AoePrediction.GetPrediction(input)
        if output.HitChance >= qr_hitchance:
            hit_count = len(Utility.GetInRange(
            output.CastPosition, enemies, r_width))
            if hit_count > bestCount:
                bestCount = hit_count
                bestPos = output.CastPosition

    return bestCount, bestPos


def r_hitcount(enemies: list[ChampionObj]):
    count = 0

    for enemy in enemies:
        if Utility.To2D(enemy.pos).distance(Utility.To2D(ball_position)) < r_width and Utility.To2D(enemy.predict_position(r_delay)).distance(Utility.To2D(ball_position)) < r_width:
            count = count + 1

    return count


def eqr_ally(pos: Vec3, allies: list[ChampionObj]):
    distance = ball_position.distance(pos)
    delay = distance / q_speed + q_delay
    best_ally = None
    best_eq_delay = hugeValue

    for ally in allies:
        distance_to_ally = ally.pos.distance(ball_position)
        delay_to_ally = distance_to_ally / e_speed + e_delay
        ally_pos = ally.predict_position(delay_to_ally)
        distance_to_pos = ally_pos.distance(pos)
        delay_to_pos = distance_to_pos / q_speed + q_delay
        eq_delay = delay_to_ally + delay_to_pos
        if delay > eq_delay and best_eq_delay > eq_delay:
            best_ally = ally
            best_eq_delay = eq_delay

    return best_ally


def r_handler(ctx: Context, enemies: list[ChampionObj], allies: list[ChampionObj]):
    player = ctx.player

    q_spell = player.Q
    e_spell = player.E
    r_spell = player.R

    if not player.can_cast_spell(r_spell):
        return False

    r_count = r_hitcount(enemies)
    qr_count, pos = qr_hitcount(player, q_spell, enemies)
    er_count, target = er_hitcount(player, e_spell, enemies, allies)

    if r_count >= r_value and r_count >= er_count and r_count >= qr_count:
        return ctx.cast_spell(r_spell, None)
    if er_count >= r_value and er_count >= qr_count:
        return ctx.cast_spell(e_spell, target.pos)
    if qr_count >= r_value:
        if er and ctx.player.can_cast_spell(e_spell):
            eqr = eqr_ally(pos, allies)
            if eqr:
                return ctx.cast_spell(e_spell, eqr.pos)
        return ctx.cast_spell(q_spell, pos)

    return False


def e_handler(ctx: Context, enemies: list[ChampionObj]):
    player = ctx.player
    e_spell = player.E
    player_pos = Utility.To2D(player.pos)
    ball_pos = Utility.To2D(ball_position)
    if not player.can_cast_spell(e_spell):
        return False

    if e_combo_dmg and not Utility.Equals(ball_pos, player_pos, 50):
        for enemy in enemies:
            delay_to_enemy = ball_position.distance(
                enemy.pos) / e_speed + e_delay
            enemy_position = Utility.To2D(
                enemy.predict_position(delay_to_enemy))
            point, is_on_segment = Utility.ClosestPointOnLineSegment(
                enemy_position, ball_pos, player_pos)
            if enemy_position.distance(point) < e_width + enemy.bounding_radius:
                return ctx.cast_spell(e_spell, player.pos)

    for enemy in enemies:
        if player.pos.distance(enemy.pos) > ball_position.distance(enemy.pos) - 150:
            return False

    return ctx.cast_spell(e_spell, player.pos)


def w_handler(ctx: Context, enemies: list[ChampionObj]):
    player = ctx.player
    w_spell = player.W

    if not player.can_cast_spell(w_spell):
        return False

    ball_pos = Utility.To2D(ball_position)
    for enemy in enemies:
        enemy_pos = Utility.To2D(enemy.pos)
        if enemy_pos.distance(ball_pos) < w_width and Utility.To2D(enemy.predict_position(r_delay)).distance(ball_pos) < w_width:
            return ctx.cast_spell(w_spell, None)

    return False


def q_handler(ctx: Context, target: ChampionObj):
    player = ctx.player
    q_spell = player.Q

    if not ctx.player.can_cast_spell(q_spell):
        return False

    input = PredictionInput(target, ball_position.clone(), player.pos.clone(
    ), True, q_delay, q_width, speed=q_speed, range=q_range, type=SkillshotType.SkillshotLine, collision=False)
    output = AoePrediction.GetPrediction(input)

    if output.HitChance >= q_combo_hitchance:
        return ctx.cast_spell(q_spell, output.CastPosition)

    return False


def set_ball_position(ctx: Context):
    global ball_position, ball_moving
    player = ctx.player
    ball_moving = False

    if player.has_buff("orianaghostself"):
        ball_position = player.pos.clone()
        return

    allies = ctx.champs.ally_to(player).near(player, ball_max_range).get()
    for ally in allies:
        if ally.has_buff('orianaghost'):
            ball_position = ally.pos.clone()
            return

    missiles = ctx.missiles.ally_to(player).get()
    for missile in missiles:
        if (missile.name == "orianaizuna" or missile.name == "orianaredact"):
            ball_moving = True
            ball_position = missile.pos.clone()
            return

    others = ctx.others.ally_to(player).get()
    for other in others:
        if other.name == "oriannaball":
            ball_position = other.pos.clone()


def draw(ctx: Context) -> None:
    global ball_draw_angle

    if not ball_draw:
        return

    draw_pos = ball_position.clone()
    t = ctx.time % 0.8
    draw_pos.y += 100.0
    draw_pos.y += -50.0*t if t < 0.4 else -(20.0 - (t - 0.4)*50.0)

    ball_draw_angle2 = ball_draw_angle - \
        315 if ball_draw_angle >= 315 else ball_draw_angle + 45
    pos1 = Vec3(draw_pos.x - 100 * math.sin(math.radians(ball_draw_angle)),
                draw_pos.y, draw_pos.z + 100 * math.cos(math.radians(ball_draw_angle)))
    pos2 = Vec3(draw_pos.x + 100 * math.sin(math.radians(ball_draw_angle)),
                draw_pos.y, draw_pos.z - 100 * math.cos(math.radians(ball_draw_angle)))
    pos3 = Vec3(draw_pos.x + 100 * math.cos(math.radians(ball_draw_angle)),
                draw_pos.y, draw_pos.z + 100 * math.sin(math.radians(ball_draw_angle)))
    pos4 = Vec3(draw_pos.x - 100 * math.cos(math.radians(ball_draw_angle)),
                draw_pos.y, draw_pos.z - 100 * math.sin(math.radians(ball_draw_angle)))
    ctx.rect_world(pos1, pos3, pos2, pos4, 5.0, Col.White)

    pos1 = Vec3(draw_pos.x - 100 * math.sin(math.radians(ball_draw_angle2)),
                draw_pos.y, draw_pos.z + 100 * math.cos(math.radians(ball_draw_angle2)))
    pos2 = Vec3(draw_pos.x + 100 * math.sin(math.radians(ball_draw_angle2)),
                draw_pos.y, draw_pos.z - 100 * math.cos(math.radians(ball_draw_angle2)))
    pos3 = Vec3(draw_pos.x + 100 * math.cos(math.radians(ball_draw_angle2)),
                draw_pos.y, draw_pos.z + 100 * math.sin(math.radians(ball_draw_angle2)))
    pos4 = Vec3(draw_pos.x - 100 * math.cos(math.radians(ball_draw_angle2)),
                draw_pos.y, draw_pos.z - 100 * math.sin(math.radians(ball_draw_angle2)))
    ctx.rect_world(pos1, pos3, pos2, pos4, 5.0, Col.White)

    if ball_draw_angle == 0:
        ball_draw_angle = 360
    else:
        ball_draw_angle -= 0.5


def valkyrie_exec(ctx: Context):
    player = ctx.player

    if player.dead or player.recalling:
        return

    set_ball_position(ctx)

    draw(ctx)

    if ball_moving or player.recalling:
        return

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).not_clone().get()

    allies = ctx.champs.ally_to(
        player).targetable().near(player, e_range).get()

    if len(enemies) == 0:
        return

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite
    target = target_selector.get_target(ctx, enemies)

    if r_auto or (is_combo and r_combo):
        if r_handler(ctx, enemies, allies):
            return
    if is_combo and e_combo:
        if e_handler(ctx, enemies):
            return
    if is_combo and q_combo:
        if q_handler(ctx, target):
            return
    if w_auto or (is_combo and w_combo):
        w_handler(ctx, enemies)
