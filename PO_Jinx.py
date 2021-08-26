"""
 ______  ______   __   __   ______   __  __   ______
/\  == \/\  __ \ /\ "-.\ \ /\  ___\ /\ \_\ \ /\  ___\
\ \  _-/\ \ \/\ \\ \ \-.  \\ \ \____\ \  __ \\ \  __\
 \ \_\   \ \_____\\ \_\\"\_\\ \_____\\ \_\ \_\\ \_____\
  \/_/    \/_____/ \/_/ \/_/ \/_____/ \/_/\/_/ \/_____/


Changelog :

v0.3 Added Ponche Prediction

v0.4 Made compatible with pred changes

To Do:

R Support

"""

from valkyrie import *
from helpers.spells import BuffType, Slot, Buffs
from helpers.flags import Orbwalker
from helpers.targeting import *
from PO_Prediction import *

target_selector = TargetSelector(0, TargetSet.Champion)

fishbones_stack = 0
fishbones_range = 525
is_fishbones = True
pow_pow_range = 600

q_combo = True
pow_pow_fullstack = False
pow_pow_aoe = True
anti_overswap_value = 60

w_combo = True
w_combo_hitchance = HitChance.High
w_auto = True
w_auto_hitchance = HitChance.Immobile
w_min_distance = True
w_min_distance_value = 900
w_width = 120
w_range = 1500
w_speed = 3300

e_combo = True
e_combo_hitchance = HitChance.High
e_auto = True
e_auto_hitchance = HitChance.Immobile
e_delay = 0.4 + 0.5
e_width = 115
e_range = 900

fight_range = 1500
include_clones = False


def valkyrie_menu(ctx: Context):
    global include_clones, e_auto_hitchance, e_combo_hitchance, w_auto_hitchance, w_combo_hitchance, w_auto, q_combo, pow_pow_fullstack, pow_pow_aoe, anti_overswap_value, w_combo, w_min_distance, w_min_distance_value, e_combo, e_auto
    ui = ctx.ui

    ui.text("Ponche Jinx V0.4")
    ui.separator()

    include_clones = ui.checkbox('Include clones', include_clones)
    ui.help("Training dummy are considered as clones")
    ui.separator()

    if ui.beginmenu("Q"):
        q_combo = ui.checkbox('Combo Q', q_combo)
        ui.separator()
        pow_pow_fullstack = ui.checkbox('Switch full stack', pow_pow_fullstack)
        ui.help("Switch to Pow-Pow if your fishbones stack are full")
        pow_pow_aoe = ui.checkbox('Pow-Pow for AOE', pow_pow_aoe)
        ui.help("Automaticly switch to Pow-Pow if you can aoe")
        anti_overswap_value = ui.sliderint(
            "Anti overswap", anti_overswap_value, 0, 120)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("W"):
        w_combo = ui.checkbox('Combo W', w_combo)
        w_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(w_combo_hitchance), w_combo_hitchance, 2)
        ui.separator()
        w_auto = ui.checkbox('Auto W', w_auto)
        w_auto_hitchance = ui.sliderenum(
            "Auto - Hit Chance", HitChance.GetHitChanceName(w_auto_hitchance), w_auto_hitchance, 2)
        ui.separator()
        w_min_distance = ui.checkbox('Use Min. distance', w_min_distance)
        w_min_distance_value = ui.sliderint(
            "Min. distance", w_min_distance_value, 0, 1450)
        ui.endmenu()
    ui.separator()

    if ui.beginmenu("E"):
        e_combo = ui.checkbox('Combo E', e_combo)
        e_combo_hitchance = ui.sliderenum(
            "Combo - Hit Chance", HitChance.GetHitChanceName(e_combo_hitchance), e_combo_hitchance, 2)
        e_auto = ui.checkbox('Auto E', e_auto)
        e_auto_hitchance = ui.sliderenum(
            "Auto - Hit Chance", HitChance.GetHitChanceName(e_auto_hitchance), e_auto_hitchance, 2)
        ui.endmenu()


def valkyrie_on_load(ctx: Context):
    global include_clones, e_auto_hitchance, e_combo_hitchance, w_auto_hitchance, w_combo_hitchance, w_auto, q_combo, pow_pow_fullstack, pow_pow_aoe, anti_overswap_value, w_combo, w_min_distance, w_min_distance_value, e_combo, e_auto

    cfg = ctx.cfg

    include_clones = cfg.get_bool('include_clones', include_clones)

    q_combo = cfg.get_bool('q_combo', q_combo)
    pow_pow_fullstack = cfg.get_bool(
        'pow_pow_fullstack', pow_pow_fullstack)
    pow_pow_aoe = cfg.get_bool('pow_pow_aoe', pow_pow_aoe)
    anti_overswap_value = cfg.get_int(
        'anti_overswap_value', anti_overswap_value)

    w_combo = cfg.get_bool('w_combo', w_combo)
    w_combo_hitchance = cfg.get_int('w_combo_hitchance', w_combo_hitchance)
    w_auto = cfg.get_bool('w_auto', w_auto)
    w_auto_hitchance = cfg.get_int('w_auto_hitchance', w_auto_hitchance)
    w_min_distance = cfg.get_bool('w_min_distance', w_min_distance)
    w_min_distance_value = cfg.get_int(
        'w_min_distance_value', w_min_distance_value)

    e_combo = cfg.get_bool('e_combo', e_combo)
    e_combo_hitchance = cfg.get_int('e_combo_hitchance', e_combo_hitchance)
    e_auto = cfg.get_bool('e_auto', e_auto)
    e_auto_hitchance = cfg.get_int('e_auto_hitchance', e_auto_hitchance)


def valkyrie_on_save(ctx: Context):
    cfg = ctx.cfg

    cfg.set_bool('include_clones', include_clones)

    cfg.set_bool('q_combo', q_combo)
    cfg.set_bool(
        'pow_pow_fullstack', pow_pow_fullstack)
    cfg.set_bool('pow_pow_aoe', pow_pow_aoe)
    cfg.set_int(
        'anti_overswap_value', anti_overswap_value)

    cfg.set_bool('w_combo', w_combo)
    cfg.set_int('w_combo_hitchance', w_combo_hitchance)
    cfg.set_bool('w_auto', w_auto)
    cfg.set_int('w_auto_hitchance', w_auto_hitchance)
    cfg.set_bool('w_min_distance', w_min_distance)
    cfg.set_int(
        'w_min_distance_value', w_min_distance_value)

    cfg.set_bool('e_combo', e_combo)
    cfg.set_int('e_combo_hitchance', e_combo_hitchance)
    cfg.set_bool('e_auto', e_auto)
    cfg.set_int('e_auto_hitchance', e_auto_hitchance)


def get_buff_count(buffs: list[Buff], buff_name: str) -> int:
    for buff in buffs:
        if buff.name == buff_name:
            return buff.count

    return 0


def get_buff_value(buffs: list[Buff], buff_name: str) -> int:
    for buff in buffs:
        if buff.name == buff_name:
            return buff.value

    return 0


def get_aoe_count(target: ChampionObj, enemies: list[ChampionObj]) -> int:
    count = 0

    for enemy in enemies:
        if target.pos.distance(enemy.pos) < 300:
            count += 1

    return count


def get_w_delay(ctx: Context, player: ChampionObj) -> float:
    w_delay = 0.6 - (int(player.bonus_atk_speed / 25) * 0.2)
    ctx.info('W delay: ' + str(w_delay))
    return w_delay


def should_swap(player: ChampionObj, target: ChampionObj, enemies: list[ChampionObj]) -> bool:
    distance_target = player.pos.distance(target.pos)
    in_pow_pow_range = distance_target < pow_pow_range + target.bounding_radius
    in_fishbones_range = distance_target < fishbones_range + target.bounding_radius
    not_overswap_range = distance_target < 525 + \
        target.bounding_radius - anti_overswap_value
    is_fullstack = fishbones_stack == 3
    can_aoe = get_aoe_count(target, enemies) > 1

    if is_fishbones:
        if not in_fishbones_range and in_pow_pow_range:
            return True
        elif pow_pow_fullstack and is_fullstack and in_pow_pow_range:
            return True
        elif pow_pow_aoe and is_fullstack and in_pow_pow_range and can_aoe:
            return True
    else:
        if not can_aoe and not is_fullstack and not_overswap_range:
            return True

    return False


def q_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj]) -> bool:
    player = ctx.player

    q_spell = player.Q

    if not ctx.player.can_cast_spell(q_spell):
        return False

    if should_swap(player, target, enemies):
        return ctx.cast_spell(q_spell, None)

    return False


def w_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj], hitchance: HitChance) -> bool:
    player = ctx.player

    w_spell = player.W

    if not ctx.player.can_cast_spell(w_spell):
        return False

    if w_min_distance:
        for enemy in enemies:
            if player.pos.distance(enemy.pos) < w_min_distance_value:
                return False

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(), True, get_w_delay(
        ctx, player), w_width, speed=w_speed, range=w_range, type=SkillshotType.SkillshotLine, collision=True, collisionableObjects=[CollisionableObjects.Minions, CollisionableObjects.Enemies])
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(w_spell, output.CastPosition)

    for enemy in enemies:
        input.Unit = enemy
        output = Prediction.GetPrediction(input)
        if output.HitChance >= hitchance:
            return ctx.cast_spell(w_spell, output.CastPosition)

    return False


def e_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj], hitchance: HitChance) -> bool:
    player = ctx.player

    e_spell = player.E

    if not ctx.player.can_cast_spell(e_spell):
        return False

    input = PredictionInput(target, player.pos.clone(), player.pos.clone(
    ), True, e_delay, w_width, range=e_range, type=SkillshotType.SkillshotCircle, collision=False)
    output = Prediction.GetPrediction(input)

    if output.HitChance >= hitchance:
        return ctx.cast_spell(e_spell, output.CastPosition)

    for enemy in enemies:
        input.Unit = enemy
        output = Prediction.GetPrediction(input)
        if output.HitChance >= hitchance:
            return ctx.cast_spell(e_spell, output.CastPosition)

    return False


def combo_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj]) -> bool:
    if e_combo and e_handler(ctx, target, enemies, e_combo_hitchance):
        return

    if q_combo and q_handler(ctx, target, enemies):
        return True

    if w_combo and w_handler(ctx, target, enemies, w_combo_hitchance):
        return True


def harass_handler(ctx: Context, target: ChampionObj, enemies: list[ChampionObj]) -> bool:
    if e_auto and e_handler(ctx, target, enemies, e_auto_hitchance):
        return

    if w_auto and w_handler(ctx, target, enemies, w_auto_hitchance):
        return True


def update_state(player: ChampionObj) -> None:
    global pow_pow_range, is_fishbones, fishbones_stack, fishbones_range

    q_spell = player.spells[Slot.Q]
    pow_pow_range = q_spell.lvl * 25 + 600
    fishbones_range = 525

    player_buffs = player.buffs

    fishbones_stack = get_buff_count(player_buffs, 'jinxqramp')

    if player.has_item(3094) and get_buff_value(player_buffs, 'itemstatikshankcharge') == 100:
        fishbones_range += 150
        pow_pow_range += 150

    is_fishbones = player.atk_range == fishbones_range


def valkyrie_exec(ctx: Context):
    player = ctx.player

    if player.dead or player.recalling or Orbwalker.Attacking:
        return

    if include_clones:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).get()
    else:
        enemies = ctx.champs.enemy_to(
            player).targetable().near(player, fight_range).not_clone().get()

    if len(enemies) == 0:
        return

    update_state(ctx.player)

    target = target_selector.get_target(ctx, enemies)
    is_combo = Orbwalker.CurrentMode == Orbwalker.ModeKite

    if harass_handler(ctx, target, enemies):
        return

    if is_combo:
        combo_handler(ctx, target, enemies)
