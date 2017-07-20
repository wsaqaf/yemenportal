class ApplicationPolicy
  attr_reader :current_user, :record

  def initialize(current_user, record)
    @current_user = current_user
    @record = record
  end

  def login?
    current_user
  end

  def member?
    current_user && current_user.role.member?
  end

  def admin?
    current_user && current_user.role.admin?
  end

  def moderator?
    current_user && (current_user.role.moderator? || current_user.role.admin?)
  end
end
