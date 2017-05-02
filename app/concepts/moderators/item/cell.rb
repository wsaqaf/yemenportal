class Moderators::Item::Cell < Application::Cell
  STATE_LIST = { moderator: "moderator", invited: "invited_moderator" }.freeze
  property :email, :first_name, :last_name, :invitation_sent_at, :invitation_accepted_at, :role

  private

  def invite_accepted?
    if invitation_sent_at
      invitation_accepted_at.present? || invitation_sent_at > Time.now - 1.hour
    else
      true
    end
  end

  def full_name
    "#{last_name} #{first_name}"
  end

  def status
    if role.moderator? && (invitation_accepted_at || !invitation_sent_at)
      STATE_LIST[:moderator]
    elsif role.moderator?
      STATE_LIST[:invited]
    end
  end
end
