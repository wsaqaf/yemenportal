class UserPolicy < ApplicationPolicy
  def index?
    current_user.admin?
  end

  def change_role?
    current_user.admin?
  end
end
