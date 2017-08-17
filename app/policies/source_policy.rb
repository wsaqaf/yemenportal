class SourcePolicy < ApplicationPolicy
  def create?
    admin?
  end

  def approve?
    admin? || moderator?
  end

  class Scope < BaseScope
    def resolve
      if current_user && (current_user.moderator? || current_user.admin?)
        scope
      else
        scope.approved
      end
    end
  end
end
