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

  class BaseScope
    attr_reader :current_user, :scope

    def initialize(current_user, scope)
      @current_user = current_user
      @scope = scope
    end
  end
end
