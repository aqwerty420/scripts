"""
 ______  ______   __   __   ______   __  __   ______    
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\   
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\   
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\ 
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/ 
                                   

Changelog :

v0.3 Added Q fix

v0.4 Q fix now work with phantom dancer, Q - E added

v0.45 Fixed mistake in Q - E

v0.5 Added E to interrupt, Improved Q logic

v0.51 Fixed E interrupt

TO_DO :

Tell me

"""

from valkyrie import *
import math
from helpers.flags import Orbwalker, EvadeFlags
from helpers.spells import Slot
from helpers.targeting import *
from time import time

target_selector = TargetSelector(0, TargetSet.Champion)

q_combo = True
q_to_e = True
q_to_e_bypass = True
q_prevent_tower = True
q_prevent_too_far = True
q_prevent_too_close = True
q_close_value = 300
q_angle_step = 20
q_range = 300

e_combo = True
e_auto = True
e_interrupt = True
e_range = 550
e_target_only = False
e_push_distance = 450
e_speed = 2000
e_delay = 0.25

r_combo = True
r_min_enemies = True
r_min_enemies_value = 3
r_min_enemies_range = 600
r_min_allies = True
r_min_allies_value = 2
r_min_allies_range = 1000

include_clones = False

fight_range = 1500
dashing = False

interruptibles = [
    'absolutezero',
    'alzaharnethergrasp',
    'caitlynaceinthehole',
    'crowstorm',
    'destiny',
    'drainChannel',
    'galioIdolofdurand',
    'infiniteduress',
    'karthusfallenone',
    'katarinar',
    'lucianr',
    'meditate',
    'missfortunebullettime',
    'pantheonrjump',
    'pantheonrfall',
    'reapthewhirlwind',
    'shenstandunited',
    'urgotswap2',
    'velkozr',
    'xerathlocusofpower2'
]


def valkyrie_menu(ctx: Context):
    global e_interrupt, q_to_e_bypass, q_to_e, include_clones, r_combo, r_min_enemies, r_min_enemies_value, r_min_enemies_range, r_min_allies, r_min_allies_value, r_min_allies_range, e_combo, e_auto, e_target_only, e_push_distance, q_combo, q_prevent_tower, q_prevent_too_far, q_prevent_too_close, q_close_value
    ui = ctx.ui

    ui.text("Ponche Vayne 0.51")
    ui.separator()

    include_clones = ui.checkbox('Include clones', include_clones)
    ui.help("Training dummy are considered as clones")
    ui.separator()

    if ui.beginmenu("Q"):
        q_combo = ui.checkbox('Combo Q', q_combo)
        ui.separator()
        q_to_e = ui.checkbox('Q to E', q_to_e)
        q_to_e_bypass = ui.checkbox(
            'Q to E bypass other checks', q_to_e_bypass)
        q_prevent_tower = ui.checkbox('Prevent under tower', q_prevent_tower)
        ui.help("It won't stop you if you are already under a tower")
        q_prevent_too_far = ui.checkbox(
            'Prevent leaving AA range', q_prevent_too_far)
        q_prevent_too_close = ui.checkbox(
            'Prevent going too close to target', q_prevent_too_close)
        q_close_value = ui.sliderint("Too close value", q_close_value, 0, 1000)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("E"):
        e_interrupt = ui.checkbox('Auto E - Interrupt', e_interrupt)
        ui.separator()
        e_combo = ui.checkbox('Combo E - Stun', e_combo)
        e_auto = ui.checkbox('Auto E - Stun', e_auto)
        e_target_only = ui.checkbox('Stun target only', e_target_only)
        e_push_distance = ui.sliderint(
            "Push distance", e_push_distance, 0, 450)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("R"):
        r_combo = ui.checkbox('Combo R', r_combo)
        ui.separator()
        r_min_enemies = ui.checkbox('Require enemies in range', r_min_enemies)
        r_min_enemies_value = ui.sliderint(
            "Number of enemies", r_min_enemies_value, 1, 5)
        r_min_enemies_range = ui.sliderint(
            "Distance to enemies", r_min_enemies_range, 100, 1500)
        r_min_allies = ui.checkbox('Require allies in range', r_min_allies)
        r_min_allies_value = ui.sliderint(
            "Number of allies", r_min_allies_value, 1, 4)
        r_min_allies_range = ui.sliderint(
            "Distance to allies", r_min_allies_range, 100, 1500)
        ui.endmenu()


def valkyrie_on_load(ctx: Context):
    global e_interrupt, q_to_e_bypass, q_to_e, include_clones, r_combo, r_min_enemies, r_min_enemies_value, r_min_enemies_range, r_min_allies, r_min_allies_value, r_min_allies_range, e_combo, e_auto, e_target_only, e_push_distance, q_combo, q_prevent_tower, q_prevent_too_far, q_prevent_too_close, q_close_value

    cfg = ctx.cfg
    q_to_e_bypass = cfg.get_bool('q_to_e_bypass', q_to_e_bypass)
    q_to_e = cfg.get_bool('q_to_e', q_to_e)
    include_clones = cfg.get_bool('include_clones', include_clones)
    q_combo = cfg.get_bool('q_combo', q_combo)
    q_prevent_tower = cfg.get_bool('q_prevent_tower', q_prevent_tower)
    q_prevent_too_far = cfg.get_bool(
        'q_prevent_too_far', q_prevent_too_far)
    q_prevent_too_close = cfg.get_bool(
        'q_prevent_too_close', q_prevent_too_close)
    q_close_value = cfg.get_int('q_close_value', q_close_value)

    e_interrupt = cfg.get_bool('e_interrupt', e_interrupt)
    e_combo = cfg.get_bool('e_combo', e_combo)
    e_auto = cfg.get_bool('e_auto', e_auto)
    e_target_only = cfg.get_bool('e_target_only', e_target_only)
    e_push_distance = cfg.get_int('e_push_distance', e_push_distance)

    r_combo = cfg.get_bool('r_combo', r_combo)
    r_min_enemies = cfg.get_bool('r_min_enemies', r_min_enemies)
    r_min_enemies_value = cfg.get_int(
        'r_min_enemies_value', r_min_enemies_value)
    r_min_enemies_range = cfg.get_int(
        'r_min_enemies_range', r_min_enemies_range)
    r_min_allies = cfg.get_bool('r_min_allies', r_min_allies)
    r_min_allies_value = cfg.get_int(
        'r_min_allies_value', r_min_allies_value)
    r_min_allies_range = cfg.get_int(
        'r_min_allies_range', r_min_allies_range)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('q_to_e_bypass', q_to_e_bypass)
    cfg.set_bool('q_to_e', q_to_e)
    cfg.set_bool('include_clones', include_clones)
    cfg.set_bool('q_combo', q_combo)
    cfg.set_bool('q_prevent_tower', q_prevent_tower)
    cfg.set_bool('q_prevent_too_far', q_prevent_too_far)
    cfg.set_bool('q_prevent_too_close', q_prevent_too_close)
    cfg.set_int('q_close_value', q_close_value)

    cfg.set_bool('e_interrupt', e_interrupt)
    cfg.set_bool('e_combo', e_combo)
    cfg.set_bool('e_auto', e_auto)
    cfg.set_bool('e_target_only', e_target_only)
    cfg.set_int('e_push_distance', e_push_distance)

    cfg.set_bool('r_combo', r_combo)
    cfg.set_bool('r_min_enemies', r_min_enemies)
    cfg.set_int('r_min_enemies_value', r_min_enemies_value)
    cfg.set_int('r_min_enemies_range', r_min_enemies_range)
    cfg.set_bool('r_min_allies', r_min_allies)
    cfg.set_int('r_min_allies_value', r_min_allies_value)
    cfg.set_int('r_min_allies_range', r_min_allies_range)


def get_tumble_pos(player_pos: Vec3):
    tumble_pos = []

    for angle in range(0, 360, 20):
        tumble_pos.append(Vec3(player_pos.x + (q_range * math.cos(math.radians(angle))), player_pos.y,
                               player_pos.z + (q_range * math.sin(math.radians(angle)))))

    return tumble_pos


def get_best_tumble_pos(mouse_pos: Vec3, possible_tumble_pos: list[Vec3]):
    best_tumble_pos = None
    best_tumble_diff = 9000

    for tumble_pos in possible_tumble_pos:
        tumble_distance_diff = tumble_pos.distance(mouse_pos)
        if best_tumble_diff > tumble_distance_diff:
            best_tumble_pos = tumble_pos
            best_tumble_diff = tumble_distance_diff

    return best_tumble_pos


def is_under_tower(turrets: list[TurretObj], pos: Vec3):
    for turret in turrets:
        if pos.distance(turret.pos) <= 915:
            return True

    return False


def is_close_spot(target_pos: Vec3, pos: Vec3):
    return target_pos.distance(pos) < q_close_value


def q_respect_rules(player_pos: Vec3, attack_range: float, target: float, turrets: list[TurretObj], tumble_pos: Vec3):
    already_under_tower = is_under_tower(turrets, player_pos)
    respect_too_far = not q_prevent_too_far or not tumble_pos.distance(
        target.pos) > attack_range
    respect_under_tower = not q_prevent_tower or not is_under_tower(
        turrets, tumble_pos)
    respect_too_close = not q_prevent_too_close or not is_close_spot(
        target.pos, tumble_pos)

    return respect_too_far and (respect_under_tower or already_under_tower) and respect_too_close


def get_pos_tumble(player_pos: Vec3, player_cursor_pos: Vec3):
    normalized = Vec2(player_cursor_pos.x - player_pos.x,
                      player_cursor_pos.z - player_pos.z).normalize()

    return Vec3(player_pos.x + q_range * normalized.x, player_pos.y, player_pos.z + q_range * normalized.y)


def clean_poses_tumble(player: ChampionObj, target: ChampionObj, turrets: list[TurretObj], possible_tumble_pos: list[Vec3]):
    remaning_tumble_pos = []

    for tumble_pos in possible_tumble_pos:
        if q_respect_rules(player.pos, player.atk_range, target, turrets, tumble_pos):
            remaning_tumble_pos.append(tumble_pos)

    return remaning_tumble_pos


def can_stun(ctx: Context, from_pos: Vec3, target: ChampionObj):
    distance = from_pos.distance(target.pos)
    delay_reach = distance / e_speed + e_delay
    target_pos = target.predict_position(delay_reach)
    normalized = normalize(from_pos, target_pos)

    stun_value = 0

    for i in range(100, e_push_distance, 40):
        point = Vec3(target_pos.x + i * normalized.x,
                     target_pos.y, target_pos.z + i * normalized.z)

        if ctx.is_wall_at(point):
            stun_value += 1

    return stun_value


def can_q_stun(ctx: Context, possible_tumble_pos: list[Vec3], target: ChampionObj):
    best_stun_value = 0
    best_tumble_pos = None

    for tumble_pos in possible_tumble_pos:
        if tumble_pos.distance(target.pos) < e_range:
            continue

        stun_value = can_stun(ctx, tumble_pos, target)
        if stun_value and stun_value > best_stun_value:
            best_stun_value = stun_value
            best_tumble_pos = tumble_pos

    return best_tumble_pos


def cast_q(ctx: Context, pos: Vec3):
    q_spell = ctx.player.Q
    Orbwalker.PauseUntil = time() + 0.3
    return ctx.cast_spell(q_spell, pos)


def q_handler(ctx: Context, target: ChampionObj,  turrets: list[TurretObj]):
    player = ctx.player
    q_spell = ctx.player.Q
    e_spell = ctx.player.E

    if not ctx.player.can_cast_spell(q_spell):
        return False

    if EvadeFlags.EvadeEndTime > time():
        return cast_q(ctx, ctx.player.pos + ((EvadeFlags.EvadePoint - ctx.player.pos).normalize() * q_range))

    cursor_tumble_pos = get_pos_tumble(
        player.pos, ctx.hud.cursor_world_pos)

    possible_tumble_pos = get_tumble_pos(player.pos)

    tumble_pos = clean_poses_tumble(
        player, target, turrets, possible_tumble_pos)

    if q_to_e and (e_combo or e_auto) and ctx.player.can_cast_spell(e_spell):
        if q_to_e_bypass:
            q_stun_pos = can_q_stun(ctx, possible_tumble_pos, target)
        else:
            q_stun_pos = can_q_stun(ctx, tumble_pos, target)
        if q_stun_pos:
            return cast_q(ctx, q_stun_pos)

    if q_respect_rules(player.pos, player.atk_range, target, turrets, cursor_tumble_pos):
        return cast_q(ctx, cursor_tumble_pos)

    best_tumble_pos = get_best_tumble_pos(
        cursor_tumble_pos, tumble_pos)

    if best_tumble_pos:
        return cast_q(ctx, best_tumble_pos)

    return False


def normalize(player_pos: Vec3, target_pos: Vec3):
    return Vec3(target_pos.x - player_pos.x, target_pos.y - player_pos.y, target_pos.z - player_pos.z).normalize()


def cast_e(ctx: Context, target_pos):
    e_spell = ctx.player.E

    return ctx.cast_spell(e_spell, target_pos)


def e_stun_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj]):
    player = ctx.player
    e_spell = player.E

    if not ctx.player.can_cast_spell(e_spell):
        return False

    if player.pos.distance(target.pos) < e_range + player.bounding_radius + target.bounding_radius and can_stun(ctx, player.pos, target):
        return cast_e(ctx, target.pos)

    if e_target_only:
        return False

    for enemy in enemies:
        if player.pos.distance(enemy.pos) < e_range + player.bounding_radius + enemy.bounding_radius and can_stun(ctx, player.pos, enemy):
            return cast_e(ctx, enemy.pos)

    return False


def is_interruptible(spellName: str):
    for interruptible in interruptibles:
        if interruptible == spellName:
            return True

    return False


def e_interrupt_handler(ctx: Context, enemies: list[ChampionObj]):
    player = ctx.player
    e_spell = player.E

    if not ctx.player.can_cast_spell(e_spell):
        return False

    for enemy in enemies:
        distance = enemy.pos.distance(player.pos)
        delay_reach = distance / e_speed + e_delay
        if distance < e_range + player.bounding_radius + enemy.bounding_radius and enemy.curr_casting and is_interruptible(enemy.curr_casting.name) and enemy.curr_casting.remaining < delay_reach:
            return cast_e(ctx, enemy.pos)

    return False


def get_in_range(player_pos: Vec3, champ_list: list[ChampionObj], range: int):
    count = 0

    for champ in champ_list:
        if player_pos.distance(champ.pos) < range:
            count += 1

    return count


def r_handler(ctx: Context, enemies: list[ChampionObj], allies: list[ChampionObj]):
    player = ctx.player
    r_spell = player.spells[Slot.R]

    if not ctx.player.can_cast_spell(r_spell):
        return False

    respect_enemies = not r_min_enemies or get_in_range(
        player.pos, enemies, r_min_enemies_range) >= r_min_enemies_value
    respect_allies = not r_min_allies or get_in_range(
        player.pos, allies, r_min_allies_range) - 1 >= r_min_allies_value

    if respect_enemies and respect_allies:
        return ctx.cast_spell(r_spell, None)

    return False


def valkyrie_exec(ctx: Context):
    global dashing
    player = ctx.player

    if player.dashing:
        if not dashing:
            dashing = True
            Orbwalker.PauseUntil = time() + 0.25
            Orbwalker.LastAttacked = 0
        return
    else:
        dashing = False

    if player.dead or player.recalling or Orbwalker.Attacking or (player.curr_casting and player.curr_casting.remaining > 0):
        return

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).not_clone().get()

    turrets = ctx.turrets.enemy_to(
        player).alive().near(player.pos, fight_range).get()
    allies = ctx.champs.ally_to(
        player).alive().near(player, fight_range).not_clone().get()

    if len(enemies) == 0:
        return

    target = target_selector.get_target(ctx, enemies)

    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if e_interrupt and e_interrupt_handler(ctx, enemies):
        return

    if e_auto or (is_combo and e_combo):
        if e_stun_handler(ctx, target, enemies):
            return

    if is_combo and r_combo:
        if r_handler(ctx, enemies, allies):
            return

    if is_combo and q_combo:
        q_handler(ctx, target, turrets)
