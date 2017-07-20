class Users::Card::Cell < Application::Cell
  private

  def user
    model
  end

  delegate :member?, :moderator?, :admin?, to: :user_role

  def user_role
    user.role
  end

  def promotion_to_moderator_button
    button_to("moderator", "", method: :post, params: {user_id: user.id},
      form_class: "user-card__action-btn-wrapper", class: "user-card__action-btn button tiny")
  end

  def promotion_to_admin_button
    button_to("admin", "", method: :post, params: {user_id: user.id},
      form_class: "user-card__action-btn-wrapper", class: "user-card__action-btn button tiny")
  end

  def retire_button
    if moderator?
      button_to("Retire", "", method: :delete,
        class: "user-card__action-btn button tiny alert")
    elsif admin?
      button_to("Retire", "", method: :delete,
        class: "user-card__action-btn button tiny alert")
    end
  end
end
