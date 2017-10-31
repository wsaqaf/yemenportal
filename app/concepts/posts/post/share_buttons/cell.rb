class Posts::Post::ShareButtons::Cell < Application::Cell
  private

  def share_script_path
    ::Rails.application.secrets.socials["share_buttons"]
  end
end
