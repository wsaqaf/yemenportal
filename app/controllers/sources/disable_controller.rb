class Sources::DisableController < Sources::StateController
  private

  def new_state
    Source.approve_state.disabled
  end
end
