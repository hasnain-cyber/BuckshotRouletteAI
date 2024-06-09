from datatypes.Action import ActionType, Action, FireTargetType
from datatypes.Item import ItemType
from datatypes.State import State, BulletType


def get_undiscovered_live_bullets(state: State) -> int:
    return state.n_live_bullets - state.bullets.count(BulletType.LIVE)


def get_undiscovered_blank_bullets(state: State) -> int:
    return (len(state.bullets) - state.n_live_bullets) - state.bullets.count(BulletType.BLANK)


def get_live_bullet_prob(state: State) -> float:
    if state.bullets[0] == BulletType.LIVE:
        return 1
    elif state.bullets[0] == BulletType.BLANK:
        return 0

    undiscovered_live_bullets = get_undiscovered_live_bullets(state)
    undiscovered_blank_bullets = get_undiscovered_blank_bullets(state)

    return undiscovered_live_bullets / (undiscovered_live_bullets + undiscovered_blank_bullets)


def get_success_prob(state: State) -> (float, Action):
    if state.player.current_health <= 0:
        return 0, None
    if state.enemy.current_health <= 0:
        return 1, None

    # If there are no bullets, then the next round will start, and this round will be
    # considered as a success, to not affect the preceding state's probability
    if len(state.bullets) == 0:
        return state.player.current_health / state.max_health, None

    # List to store the success probabilities of each action
    success_probs: (float, Action) = []

    # Try firing the shotgun
    was_sawed_off = state.is_sawed_off

    # Shotgun will not be sawed off after firing, no matter what
    state.is_sawed_off = False

    # Calculate the prob of firing a live round
    live_prob = get_live_bullet_prob(state)

    # Fire on self
    # Assume live bullet
    temp_prob = 0
    if state.n_live_bullets > 0:
        state.player.current_health -= (1 + state.is_sawed_off)
        state.n_live_bullets -= 1
        temp_bullet = state.bullets.pop(0)

        state.player, state.enemy = state.enemy, state.player
        temp_prob += live_prob * (1 - get_success_prob(state)[0])
        state.player, state.enemy = state.enemy, state.player

        state.player.current_health += (1 + state.is_sawed_off)
        state.n_live_bullets += 1
        state.bullets.insert(0, temp_bullet)

    # Assume blank bullet
    if state.n_live_bullets < len(state.bullets):
        # Firing a blank round on self does not give turn to enemy
        temp_bullet = state.bullets.pop(0)
        temp_prob += (1 - live_prob) * get_success_prob(state)[0]
        state.bullets.insert(0, temp_bullet)


    success_probs.append((temp_prob, Action(ActionType.FIRE, FireTargetType.PLAYER)))

    # Fire on enemy
    # Assume live bullet
    temp_prob = 0
    if state.n_live_bullets > 0:
        state.enemy.current_health -= (1 + state.is_sawed_off)
        state.n_live_bullets -= 1
        temp_bullet = state.bullets.pop(0)

        # Check if enemy is handcuffed or not
        if not state.is_handcuffed:
            state.player, state.enemy = state.enemy, state.player
            temp_prob += live_prob * (1 - get_success_prob(state)[0])
            state.player, state.enemy = state.enemy, state.player
        else:
            state.is_handcuffed = False
            temp_prob += live_prob * get_success_prob(state)[0]
            state.is_handcuffed = True

        state.enemy.current_health += (1 + state.is_sawed_off)
        state.n_live_bullets += 1
        state.bullets.insert(0, temp_bullet)

    # Assume blank bullet
    if state.n_live_bullets < len(state.bullets):
        # Firing a blank round on enemy gives turn to enemy, unless enemy is handcuffed
        temp_bullet = state.bullets.pop(0)

        if not state.is_handcuffed:
            temp_prob += (1 - live_prob) * (1 - get_success_prob(state)[0])
        else:
            state.is_handcuffed = False
            temp_prob += (1 - live_prob) * get_success_prob(state)[0]
            state.is_handcuffed = True

        state.bullets.insert(0, temp_bullet)

    success_probs.append((temp_prob, Action(ActionType.FIRE, FireTargetType.ENEMY)))

    # Reset the sawed off state
    state.is_sawed_off = was_sawed_off

    # Try using an item
    for item in state.player.items:
        # Use item on self
        temp_prob = 0
        if item.quantity > 0:
            item.quantity -= 1

            if (item.item_type == ItemType.MAGNIFYING_GLASS) and (state.bullets[0] == BulletType.UNKNOWN):
                # Assume bullet revealed is live
                state.bullets[0] = BulletType.LIVE
                temp_prob += live_prob * get_success_prob(state)[0]
                state.bullets[0] = BulletType.UNKNOWN

                # Assume bullet revealed is blank
                state.bullets[0] = BulletType.BLANK
                temp_prob += (1 - live_prob) * get_success_prob(state)[0]
                state.bullets[0] = BulletType.UNKNOWN

            elif (item.item_type == ItemType.CIGARETTES) and (state.player.current_health < state.max_health):
                # Use item if health is less than max
                state.player.current_health += 1
                temp_prob += get_success_prob(state)[0]
                state.player.current_health -= 1

            elif item.item_type == ItemType.BEER:
                # Assume live bullet ejected
                if state.n_live_bullets > 0:
                    state.n_live_bullets -= 1
                    temp_bullet = state.bullets.pop(0)
                    temp_prob += live_prob * get_success_prob(state)[0]
                    state.n_live_bullets += 1
                    state.bullets.insert(0, temp_bullet)

                # Assume blank bullet ejected
                if state.n_live_bullets < len(state.bullets):
                    temp_bullet = state.bullets.pop(0)
                    temp_prob += (1 - live_prob) * get_success_prob(state)[0]
                    state.bullets.insert(0, temp_bullet)

            elif (item.item_type == ItemType.HANDCUFFS) and (not state.is_handcuffed):
                # Handcuff the enemy
                state.is_handcuffed = True
                temp_prob += get_success_prob(state)[0]
                state.is_handcuffed = False

            elif (item.item_type == ItemType.SAW) and (not state.is_sawed_off):
                # Saw off the shotgun
                state.is_sawed_off = True
                temp_prob += get_success_prob(state)[0]
                state.is_sawed_off = False

            elif item.item_type == ItemType.BURNER_PHONE:
                # TODO: Write logic for burner phone
                pass

            elif (item.item_type == ItemType.EXPIRED_MEDICINE) and (state.player.current_health < state.max_health):
                # Half probability of healing 2 health
                temp_player_health = state.player.current_health
                state.player.current_health = min(state.player.current_health + 2, state.max_health)
                temp_prob += 0.5 * get_success_prob(state)[0]
                state.player.current_health = temp_player_health

                # Half probability of losing 1 health
                state.player.current_health -= 1
                temp_prob += 0.5 * get_success_prob(state)[0]
                state.player.current_health += 1

            elif item.item_type == ItemType.ADRENALINE:
                # TODO: Write logic for adrenaline
                pass

            elif item.item_type == ItemType.INVERTER:
                # Assume live bullet inverted
                if state.n_live_bullets > 0:
                    state.n_live_bullets -= 1
                    temp_bullet = state.bullets[0]
                    state.bullets[0] = BulletType.BLANK
                    temp_prob += live_prob * get_success_prob(state)[0]
                    state.n_live_bullets += 1
                    state.bullets[0] = temp_bullet

                # Assume blank bullet inverted
                if state.n_live_bullets < len(state.bullets):
                    temp_bullet = state.bullets[0]
                    state.bullets[0] = BulletType.LIVE
                    temp_prob += (1 - live_prob) * get_success_prob(state)[0]
                    state.bullets[0] = temp_bullet

            item.quantity += 1

        success_probs.append((temp_prob, Action(ActionType.USE_ITEM, item)))

    # Return the action with the highest success probability
    return max(success_probs, key=lambda x: x[0])


class MarkovChain:
    pass
