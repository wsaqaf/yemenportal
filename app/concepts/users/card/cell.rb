class Users::Card::Cell < Application::Cell
  private

  def user
    model
  end

  delegate :member?, :moderator?, :admin?, to: :user_role
  delegate :invitation_sent_at, :invitation_accepted_at, to: :user

  def user_role
    user.role
  end

  def invited?
    invitation_accepted_at.blank? && invitation_sent_at.present?
  end

  def resend_invite_button
    button_to(st("resend_invite"), user_invitation_path, method: :post,
      params: { user: { email: user.email } }, form_class: "user-card__action-btn-wrapper",
      class: "user-card__invitation-resend button tiny secondary")
  end

  def promotion_to_moderator_button
    button_to(st("moderator"), user_moderator_permissions_path(user), method: :post,
      params: { user_id: user.id }, form_class: "user-card__action-btn-wrapper",
      class: "user-card__action-btn button tiny")
  end

  def promotion_to_admin_button
    button_to(st("admin"), user_admin_permissions_path(user), method: :post,
      params: { user_id: user.id }, form_class: "user-card__action-btn-wrapper",
      class: "user-card__action-btn button tiny")
  end

  def retire_button
    if moderator?
      button_to(st("retire_button"), user_moderator_permissions_path(user), method: :delete,
        class: "user-card__action-btn button tiny alert")
    elsif admin?
      button_to(st("retire_button"), user_admin_permissions_path(user), method: :delete,
        class: "user-card__action-btn button tiny alert")
    end
  end
end
