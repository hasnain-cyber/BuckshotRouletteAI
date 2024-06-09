from datatypes.Action import ActionType, Action, FireTargetType
from datatypes.State import State, BulletType


def get_live_bullet_prob(state: State) -> float:
    if state.bullets[0] == BulletType.LIVE:
        return 1
    elif state.bullets[0] == BulletType.BLANK:
        return 0

    undiscovered_live_bullets = state.n_live_bullets - state.bullets.count(
        BulletType.LIVE)
    undiscovered_blank_bullets = (
                                         len(state.bullets) - state.n_live_bullets) - state.bullets.count(
        BulletType.BLANK)

    return undiscovered_live_bullets / (
            undiscovered_live_bullets + undiscovered_blank_bullets)


def get_success_prob(state: State) -> (float, Action):
    if state.player.current_health <= 0:
        return 0, None
    if state.enemy.current_health <= 0:
        return 1, None

    # If there are no bullets, then the next round will start, and this round will be
    # considered as a success, to not affect the preceding state's proboability
    if len(state.bullets) == 0:
        return 1, None

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

        # Check if enemy is handcuffed or not
        if not state.is_handcuffed:
            state.player, state.enemy = state.enemy, state.player
            temp_prob += live_prob * (1 - get_success_prob(state)[0])
            state.player, state.enemy = state.enemy, state.player
        else:
            state.is_handcuffed = False
            temp_prob += live_prob * get_success_prob(state)[0]
            state.is_handcuffed = True

        state.player.current_health += (1 + state.is_sawed_off)
        state.n_live_bullets += 1

    # Assume blank bullet
    if state.n_live_bullets < len(state.bullets):
        # Firing a blank round on self does not give turn to enemy
        temp_prob += (1 - live_prob) * get_success_prob(state)[0]

    success_probs.append((temp_prob, Action(ActionType.FIRE, FireTargetType.PLAYER)))

    # Fire on enemy
    # Assume live bullet
    temp_prob = 0
    if state.n_live_bullets > 0:
        state.enemy.current_health -= (1 + state.is_sawed_off)
        state.n_live_bullets -= 1

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

    # Assume blank bullet
    if state.n_live_bullets < len(state.bullets):
        # Firing a blank round on enemy gives turn to enemy, unless enemy is handcuffed
        if not state.is_handcuffed:
            temp_prob += (1 - live_prob) * (1 - get_success_prob(state)[0])
        else:
            state.is_handcuffed = False
            temp_prob += (1 - live_prob) * get_success_prob(state)[0]
            state.is_handcuffed = True

    success_probs.append((temp_prob, Action(ActionType.FIRE, FireTargetType.ENEMY)))

    state.is_sawed_off = was_sawed_off

    # Try using an item
    for item in state.player.items:
        # Use item on self
        temp_prob = 0
        if item.quantity > 0:
            item.quantity -= 1

            # Check if enemy is handcuffed or not
            if not state.is_handcuffed:
                state.player, state.enemy = state.enemy, state.player
                temp_prob += (1 - get_success_prob(state)[0])
                state.player, state.enemy = state.enemy, state.player
            else:
                state.is_handcuffed = False
                temp_prob += get_success_prob(state)[0]
                state.is_handcuffed = True

            item.quantity += 1

        success_probs.append((temp_prob, Action(ActionType.USE_ITEM, item)))

    # Return the action with the highest success probability
    return max(success_probs, key=lambda x: x[0])


class MarkovChain:
    pass
