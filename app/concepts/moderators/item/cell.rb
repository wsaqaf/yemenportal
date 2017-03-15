class Moderators::Item::Cell < Application::Cell
  property :email, :first_name, :last_name

  private

  def full_name
    "#{last_name} #{first_name}"
  end
end
