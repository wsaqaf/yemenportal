class ApplicationPolicy
  attr_reader :user, :record

  def initialize(user, record)
    @user = user
    @record = record
  end

  def admin?
    user && user.role.admin?
  end

  def moderator?
    user && (user.role.moderator? || user.role.admin?)
  end
end
